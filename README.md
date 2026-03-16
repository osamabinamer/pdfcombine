# PDFStudio - Modern PDF & Image Merger

Combine multiple PDF and image files into a single PDF—fast, free, and beautifully simple.

🌟 **Try it live:** [https://pdfcombine-omega.vercel.app/](https://pdfcombine-omega.vercel.app/)

---

## Features

- **Merge PDFs & Images:** Upload PDFs, JPGs, JPEGs, and PNGs in any combination
- **File Previews:** See thumbnails of your PDFs and images before merging
- **Drag-and-Drop Reordering:** Rearrange files in the order you want before merging
- **Remove Files:** Easily remove files from the queue before processing
- **Custom Output Filename:** Specify the name of your merged PDF
- **File Size Display:** See individual and total file sizes before merging
- **Dark Mode:** Toggle between light and dark themes with persistent preference
- **Modern, Responsive UI:** Clean design that works on desktop and mobile
- **Instant Download:** Get your merged PDF immediately—no registration required
- **Secure:** Files are processed in-memory and not stored on the server

---

## Tech Stack

**Backend:**
- [FastAPI](https://fastapi.tiangolo.com/) – Modern async Python web framework
- [Uvicorn](https://www.uvicorn.org/) – ASGI server
- [Pydantic](https://docs.pydantic.dev/) – Data validation
- [pypdf](https://pypdf.readthedocs.io/) – PDF manipulation
- [Pillow](https://python-pillow.org/) – Image processing
- [Mangum](https://mangum.io/) – ASGI to Lambda adapter (for serverless)
- [APScheduler](https://apscheduler.readthedocs.io/) – Background task scheduling

**Frontend:**
- [Bootstrap 5](https://getbootstrap.com/) – Responsive UI framework
- [PDF.js](https://mozilla.github.io/pdf.js/) – PDF preview rendering
- [SortableJS](https://sortablejs.github.io/Sortable/) – Drag-and-drop reordering
- [Toastify.js](https://apvarun.github.io/toastify-js/) – Toast notifications
- Vanilla JavaScript with localStorage for dark mode persistence

**Deployment:**
- [Vercel](https://vercel.com/) – Serverless deployment platform

---

## Getting Started Locally

### 1. Clone the Repository
```bash
git clone https://github.com/osamabinamer/pdfcombine.git
cd pdfcombine
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 3000
```

Then open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Deployment

This app is deployed on **Vercel** using serverless functions. To deploy your own:

1. Push to your GitHub repository
2. Connect your repo to [Vercel](https://vercel.com/)
3. Vercel will automatically build and deploy from the `main` branch

The app uses:
- `vercel.json` for build configuration
- `api/index.py` as the serverless function handler
- `requirements.txt` for Python dependencies

---

## Architecture

```
pdfcombine/
├── main.py                 # FastAPI application
├── app.py                  # Entry point (deleted after migration)
├── requirements.txt        # Python dependencies
├── vercel.json             # Vercel configuration
├── api/
│   └── index.py            # Serverless handler
├── templates/
│   └── index.html          # UI with dark mode
└── output/                 # Temporary file storage
```

---

## Contributing

Pull requests and feature suggestions are welcome!  
[Open an issue](https://github.com/osamabinamer/pdfcombine/issues) to report bugs or suggest features.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Future Enhancements

- ✅ File preview and removal *(implemented)*
- ✅ Custom output filename *(implemented)*
- ✅ Dark mode *(implemented)*
- Password protection for merged PDFs
- Support for Word documents and Excel sheets
- Real-time merge progress tracking
- Batch processing with API endpoint
- Email delivery of merged PDFs

---

**Enjoy merging your PDFs and images!** 📄✨
