@echo off
REM FastAPI 服务启动脚本 (Windows批处理)

echo ============================================================
echo Starting FastAPI Server
echo ============================================================
echo.
echo Service URL: http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
echo ReDoc: http://127.0.0.1:8000/redoc
echo.
echo Press Ctrl+C to stop the service
echo ============================================================
echo.

python -m uvicorn app.api_main:app --reload --host 127.0.0.1 --port 8000

pause
