@echo off
echo ==========================================
echo     Stock Analyzer Pro - Windows Setup
echo ==========================================
echo.
echo Installing Python dependencies...
python -m venv stock_env
call stock_env\Scripts\activate.bat
pip install yfinance pandas matplotlib
echo.
echo Creating launcher script...
echo @echo off > run_stock_analyzer.bat
echo cd /d "%%~dp0" >> run_stock_analyzer.bat
echo call stock_env\Scripts\activate.bat >> run_stock_analyzer.bat
echo python stock_analyzer_gui.py >> run_stock_analyzer.bat
echo.
echo Setup complete!
echo.
echo To create desktop shortcut:
echo 1. Right-click 'run_stock_analyzer.bat'
echo 2. Send to ^> Desktop (create shortcut)
echo 3. Right-click desktop shortcut ^> Properties
echo 4. Change Icon ^> Browse ^> Select 'stock_analyzer_icon.ico'
echo 5. Rename shortcut to 'Stock Analyzer Pro'
echo.
pause
