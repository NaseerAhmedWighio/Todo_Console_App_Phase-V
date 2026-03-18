# How to Run the Backend Server

## ✅ Recommended Commands

### Option 1: Using uv (Recommended)
```bash
cd backend
uv run python -m uvicorn main:app --reload --port 7860
```

### Option 2: Using the Start Script
```bash
cd backend
start.bat
```

### Option 3: Using Python directly
```bash
cd backend
python -m uvicorn main:app --reload --port 7860
```

### Option 4: Using main.py
```bash
cd backend
python main.py
```

---

## ❌ Don't Use This (Causes Error)
```bash
# WRONG - uv run doesn't work with module syntax
uv run uvicorn main:app --reload --port 7860
```

The error occurs because `uv run` expects a script file path, not a module name like `uvicorn main:app`.

---

## Quick Test

After starting the server, verify it's running:
```bash
curl http://localhost:7860/health
```

Expected output:
```json
{"status":"healthy"}
```

---

## API Documentation

Once running, view interactive docs at:
**http://localhost:7860/docs**
