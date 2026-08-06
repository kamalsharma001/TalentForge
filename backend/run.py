"""
TalentForge — entry point.
Run locally:  python run.py
Production:   gunicorn "app.main:app" -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT
"""

from app.main import app

if __name__ == "__main__":
    import uvicorn
    # Use reload=True in development
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=True)
