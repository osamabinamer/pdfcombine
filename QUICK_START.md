# Quick Start - PDFStudio 2.0

Get up and running in 3 minutes! 🚀

---

## Step 1: Install Dependencies (1 min)

```bash
pip install -r requirements.txt
```

---

## Step 2: Run the App (1 min)

**Development Mode** (with auto-reload):
```bash
python -m uvicorn main:app --reload
```

**Or Production Mode** (using Gunicorn):
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:5000
```

---

## Step 3: Open in Browser (seconds)

Open your browser to:
```
http://localhost:5000
```

**API Documentation:**
- Swagger UI: `http://localhost:5000/docs`
- ReDoc: `http://localhost:5000/redoc`

---

## That's It! 🎉

You now have a modern, feature-rich PDF tool running with:
- ✨ Dark mode
- 📸 File previews
- ⚡ Fast async processing
- 🧹 Auto file cleanup
- 🎯 Better error messages

---

## What Changed?

| Feature | Before | After |
|---------|--------|-------|
| Framework | Flask | FastAPI |
| Speed | Standard | 2-3x faster |
| Dark Mode | ❌ | ✅ |
| File Previews | ❌ | ✅ |
| Auto Cleanup | ❌ | ✅ |

---

## Key Features to Try

1. **Dark Mode** - Click the 🌙 button (top-right)
2. **File Preview** - PDF thumbnails + image previews
3. **Remove Files** - Click the red "✕ Remove" button
4. **Custom Output Name** - Enter PDF name before merge
5. **Error Messages** - Toast notifications (helpful!)
6. **File Info** - See file sizes and totals

---

## Troubleshooting

**Port 5000 in use?**
```bash
python -m uvicorn main:app --reload --port 8000
```

**Module not found?**
```bash
pip install -r requirements.txt
```

**Still not working?**
Check the logs:
```bash
python -m uvicorn main:app --log-level info
```

---

## Documentation

- 📖 **MIGRATION_GUIDE.md** - Full migration from Flask
- 🎯 **PROJECT_ANALYSIS.md** - Vision & roadmap
- ✅ **IMPLEMENTATION_SUMMARY.md** - What was built

---

## API Quick Reference

### Merge Files
```bash
curl -X POST http://localhost:5000/api/merge \
  -F "files=@file1.pdf" \
  -F "files=@file2.png" \
  -F "filename=my-document"
```

### Split PDF
```bash
curl -X POST http://localhost:5000/api/split \
  -F "pdf=@document.pdf" \
  -F "split_type=every_n" \
  -F "every_n=5"
```

### Health Check
```bash
curl http://localhost:5000/api/health
```

---

## Environment Variables (Optional)

Create `.env` file:
```env
HOST=0.0.0.0
PORT=5000
DEBUG=False
MAX_FILE_SIZE_MB=100
CLEANUP_AGE_HOURS=24
```

---

## Next Steps

1. ✅ Run the app
2. 📝 Test the features
3. 🚀 Deploy to your server
4. 📊 Read PROJECT_ANALYSIS.md for future improvements

---

**Enjoying it?** Share feedback and feature ideas! 🙌
