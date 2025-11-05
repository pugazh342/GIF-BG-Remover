@echo off
echo Installing GIF Background Remover Dependencies...

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing packages...
pip install -r requirements.txt

echo.
echo Installation complete!
echo.
echo To test the installation, run:
echo   python main.py --check-deps
echo   python -m pytest tests/ -v
pause