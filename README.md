# Stock Analyzer Premium

A professional desktop stock market analysis application with interactive charts and technical indicators.

## Features
- TradingView-inspired dark theme interface
- Real-time stock data from Yahoo Finance
- Interactive crosshair tooltips with detailed data
- Technical indicators: 20-day MA, 50-day MA, RSI
- Smart buy/sell/hold recommendations
- Scrollable high-resolution charts
- Professional trading signals

### Manual Installation - In command prompt
Inatall python on your PC first and then install tkinter using the command - "pip install tk"
Then check if you installed it correctly using python -c "import tkinter; tkinter._test()"
If a small window pops up, Tkinter is working properly. 🎉
After all of that is done, follow the steps down below.
```bash
git clone https://github.com/spacem0nkey666/stock-analyzer.git
cd stock-analyzer
python3 -m venv stock_env
source stock_env/bin/activate  # Windows: stock_env\Scripts\activate
pip install -r requirements.txt
python3 stock_analyzer_gui.py

## To create an icon shortcut for the app

### Windows Users
1. Download this repository (Code > Download ZIP)
2. Extract to a folder
3. Double-click `setup_windows.bat`
4. Follow on-screen instructions to create desktop shortcut

### Linux/Ubuntu Users
1. Clone or download this repository
2. Run: `./setup_linux.sh`
3. App will appear in your applications menu

