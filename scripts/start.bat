@echo off
cd /d "%~dp0\.."

if not exist .venv (
  echo Missing .venv. Run scripts\setup.bat first.
  exit /b 1
)

call .venv\Scripts\activate.bat
set PYTHONPATH=backend
start "fakao-backend" cmd /k "uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000"

cd frontend
call npm run dev
