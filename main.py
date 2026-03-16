"""
PDFStudio - Modern PDF Merge & Split Tool
Built with FastAPI for high-performance async processing
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import os
import asyncio
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from io import BytesIO
import zipfile
import time

# PDF & Image processing
from pypdf import PdfWriter, PdfReader
from PIL import Image

# Scheduling for cleanup
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# ========== LOGGING SETUP ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== CONFIGURATION ==========
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
OUTPUT_DIR = Path('output')
OUTPUT_DIR.mkdir(exist_ok=True)
CLEANUP_AGE_HOURS = 24

# ========== PYDANTIC MODELS ==========
class MergeRequest(BaseModel):
    """Validation model for merge request metadata"""
    filename: str = Field("merged", min_length=1, max_length=100)
    
    @validator('filename')
    def filename_valid(cls, v):
        # Remove extension if provided
        if v.endswith('.pdf'):
            v = v[:-4]
        # Sanitize filename
        v = "".join(c for c in v if c.isalnum() or c in (' ', '-', '_')).strip()
        if not v:
            raise ValueError("Invalid filename")
        return v


class SplitRequest(BaseModel):
    """Validation model for split request"""
    split_type: str = Field(..., pattern="^(all_pages|range|every_n)$")
    page_range: Optional[str] = None
    every_n: Optional[int] = Field(None, ge=1)
    
    @validator('page_range')
    def validate_page_range(cls, v, values):
        if values.get('split_type') == 'range' and v:
            parts = v.strip().split('-')
            if len(parts) != 2:
                raise ValueError("Page range must be in format 'start-end'")
            try:
                start, end = map(int, parts)
                if start < 1 or start > end:
                    raise ValueError("Invalid page range")
            except ValueError:
                raise ValueError("Page range must contain valid integers")
        return v


# ========== FASTAPI APP SETUP ==========
app = FastAPI(
    title="PDFStudio API",
    description="Modern PDF manipulation API with async processing",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
# app.mount("/static", StaticFiles(directory="static"), name="static")


# ========== UTILITY FUNCTIONS ==========
def allowed_file(filename: str) -> bool:
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


async def cleanup_old_files():
    """Remove temporary files older than CLEANUP_AGE_HOURS"""
    try:
        cutoff_time = time.time() - (CLEANUP_AGE_HOURS * 3600)
        if OUTPUT_DIR.exists():
            for file_path in OUTPUT_DIR.glob('*'):
                if file_path.is_file() and os.path.getmtime(file_path) < cutoff_time:
                    file_path.unlink()
                    logger.info(f"Cleaned up old file: {file_path.name}")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


def validate_file_size(file_size: int) -> bool:
    """Validate that file doesn't exceed max size"""
    return file_size <= MAX_FILE_SIZE


# ========== BACKGROUND SCHEDULER ==========
scheduler = BackgroundScheduler()
IS_SERVERLESS = os.getenv('VERCEL') == '1'  # Disable scheduler in serverless

@app.on_event("startup")
async def startup_event():
    """Start background cleanup scheduler on app startup"""
    if not IS_SERVERLESS:
        try:
            scheduler.add_job(
                cleanup_old_files,
                trigger=IntervalTrigger(hours=1),
                id='cleanup_job',
                name='Cleanup old temp files',
                replace_existing=True
            )
            scheduler.start()
            logger.info("Background scheduler started")
        except Exception as e:
            logger.warning(f"Could not start scheduler: {e}")
    else:
        logger.info("Running in serverless environment - background scheduler disabled")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop scheduler on app shutdown"""
    if not IS_SERVERLESS and scheduler.running:
        scheduler.shutdown()
        logger.info("Background scheduler stopped")


# ========== ERROR HANDLERS ==========
class PdfProcessingError(Exception):
    """Custom exception for PDF processing errors"""
    pass


@app.exception_handler(PdfProcessingError)
async def pdf_processing_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"message": str(exc)}
    )


@app.exception_handler(ValueError)
async def value_error_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"message": str(exc)}
    )


# ========== ROUTES ==========

@app.get("/")
async def serve_index():
    """Serve the main HTML page"""
    return FileResponse("templates/index.html", media_type="text/html")


@app.post("/api/merge")
async def merge_pdfs(
    files: List[UploadFile] = File(...),
    order: str = Form(""),
    filename: str = Form("merged"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Merge multiple PDF/image files into a single PDF
    
    Args:
        files: List of PDF/image files to merge
        order: Comma-separated list of filenames in order
        filename: Output filename (without .pdf extension)
        background_tasks: For cleanup after response
    
    Returns:
        PDF file as download
    """
    try:
        if not files or len(files) == 0:
            raise PdfProcessingError("No files provided")
        
        # Validate and read files
        file_list = []
        for file in files:
            # Check file extension
            if not allowed_file(file.filename):
                raise PdfProcessingError(
                    f"File '{file.filename}' has unsupported format. "
                    f"Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
                )
            
            # Read file content
            content = await file.read()
            if len(content) == 0:
                raise PdfProcessingError(f"File '{file.filename}' is empty")
            
            if not validate_file_size(len(content)):
                raise PdfProcessingError(
                    f"File '{file.filename}' exceeds maximum size of 100MB"
                )
            
            file_list.append({
                'filename': file.filename,
                'content': content,
                'type': file.content_type
            })
        
        logger.info(f"Processing merge request: {len(file_list)} files")
        
        # Reorder files if order specified
        if order:
            order_list = [name.strip() for name in order.split(',') if name.strip()]
            file_dict = {f['filename']: f for f in file_list}
            try:
                file_list = [file_dict[name] for name in order_list if name in file_dict]
            except KeyError:
                logger.warning("Invalid order specified, using original order")
        
        # Merge files
        writer = PdfWriter()
        
        for file_data in file_list:
            ext = file_data['filename'].rsplit('.', 1)[-1].lower()
            
            try:
                if ext == 'pdf':
                    reader = PdfReader(BytesIO(file_data['content']))
                    for page in reader.pages:
                        writer.add_page(page)
                elif ext in {'jpg', 'jpeg', 'png'}:
                    # Convert image to PDF
                    image = Image.open(BytesIO(file_data['content'])).convert('RGB')
                    img_pdf_io = BytesIO()
                    image.save(img_pdf_io, format='PDF')
                    img_pdf_io.seek(0)
                    reader = PdfReader(img_pdf_io)
                    for page in reader.pages:
                        writer.add_page(page)
            except Exception as e:
                raise PdfProcessingError(f"Error processing '{file_data['filename']}': {str(e)}")
        
        # Save output
        output_filename = f"{filename}.pdf"
        output_path = OUTPUT_DIR / output_filename
        
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        logger.info(f"Successfully created merged PDF: {output_filename}")
        
        # Schedule cleanup of output file after download completes
        background_tasks.add_task(lambda: None)  # Placeholder
        
        return FileResponse(
            output_path,
            media_type='application/pdf',
            filename=output_filename
        )
    
    except PdfProcessingError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during merge: {e}", exc_info=True)
        raise PdfProcessingError("An unexpected error occurred during merging")


@app.post("/api/split")
async def split_pdf(
    pdf: UploadFile = File(...),
    split_type: str = Form("all_pages"),
    page_range: Optional[str] = Form(None),
    every_n: Optional[int] = Form(None)
):
    """
    Split a PDF into multiple files
    
    Args:
        pdf: PDF file to split
        split_type: Type of split (all_pages, range, every_n)
        page_range: Page range for range split (e.g., "3-7")
        every_n: Number of pages for every_n split
    
    Returns:
        ZIP file containing split PDFs
    """
    try:
        if not pdf.filename.lower().endswith('.pdf'):
            raise PdfProcessingError("Please upload a valid PDF file")
        
        content = await pdf.read()
        if not content:
            raise PdfProcessingError("PDF file is empty")
        
        # Parse PDF
        try:
            reader = PdfReader(BytesIO(content))
        except Exception as e:
            raise PdfProcessingError(f"Invalid PDF file: {str(e)}")
        
        total_pages = len(reader.pages)
        if total_pages == 0:
            raise PdfProcessingError("PDF has no pages")
        
        logger.info(f"Splitting PDF with {total_pages} pages, type: {split_type}")
        
        output_files = []
        
        if split_type == "all_pages":
            # Split every page
            for i, page in enumerate(reader.pages):
                writer = PdfWriter()
                writer.add_page(page)
                output_io = BytesIO()
                writer.write(output_io)
                output_io.seek(0)
                output_files.append((f'page_{i+1:04d}.pdf', output_io.getvalue()))
        
        elif split_type == "range":
            # Split by page range
            if not page_range:
                raise PdfProcessingError("Page range is required for range split")
            
            try:
                start, end = map(int, page_range.strip().split('-'))
                if start < 1 or end > total_pages or start > end:
                    raise ValueError()
            except (ValueError, AttributeError):
                raise PdfProcessingError(
                    f"Invalid page range. Must be between 1-{total_pages}"
                )
            
            writer = PdfWriter()
            for i in range(start - 1, end):
                writer.add_page(reader.pages[i])
            output_io = BytesIO()
            writer.write(output_io)
            output_io.seek(0)
            output_files.append((f'pages_{start}_to_{end}.pdf', output_io.getvalue()))
        
        elif split_type == "every_n":
            # Split every N pages
            if not every_n or every_n < 1:
                raise PdfProcessingError("Valid number of pages is required")
            
            for i in range(0, total_pages, every_n):
                writer = PdfWriter()
                for j in range(i, min(i + every_n, total_pages)):
                    writer.add_page(reader.pages[j])
                output_io = BytesIO()
                writer.write(output_io)
                output_io.seek(0)
                end_page = min(i + every_n, total_pages)
                output_files.append(
                    (f'pages_{i+1}_to_{end_page}.pdf', output_io.getvalue())
                )
        
        else:
            raise PdfProcessingError(f"Unknown split type: {split_type}")
        
        # Create ZIP
        zip_io = BytesIO()
        with zipfile.ZipFile(zip_io, 'w', zipfile.ZIP_DEFLATED) as zf:
            for filename, data in output_files:
                zf.writestr(filename, data)
        
        zip_io.seek(0)
        logger.info(f"Created ZIP with {len(output_files)} files")
        
        return StreamingResponse(
            iter([zip_io.getvalue()]),
            media_type='application/zip',
            headers={'Content-Disposition': 'attachment; filename="split_pdfs.zip"'}
        )
    
    except PdfProcessingError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during split: {e}", exc_info=True)
        raise PdfProcessingError("An unexpected error occurred during splitting")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }


# ========== MAIN ==========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        log_level="info"
    )
