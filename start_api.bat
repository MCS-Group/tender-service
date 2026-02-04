@echo off
echo Starting Sentiment API Server...
echo.
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8003