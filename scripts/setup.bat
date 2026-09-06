@echo off
cd /d "%~dp0\.."

python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt

cd frontend
call npm install
cd ..
echo Setup complete. Run scripts\start.bat
