@echo off
echo Setting up GIF Background Remover Environment...

echo Creating virtual environment...
python -m venv gif_bg_remover_env

echo Activating virtual environment...
call gif_bg_remover_env\Scripts\activate

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo Setup complete!
echo.
echo To activate the environment in the future, run:
echo   gif_bg_remover_env\Scripts\activate
echo.
echo To test the installation, run:
echo   python main.py --check-deps
pause