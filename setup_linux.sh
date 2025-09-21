#!/bin/bash
echo "=========================================="
echo "    Stock Analyzer Pro - Linux Setup"
echo "=========================================="
echo
echo "Installing Python dependencies..."
python3 -m venv stock_env
source stock_env/bin/activate
pip install yfinance pandas matplotlib
echo
echo "Creating launcher script..."
cat > run_stock_analyzer.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source stock_env/bin/activate
python3 stock_analyzer_gui.py
EOF
chmod +x run_stock_analyzer.sh
echo
echo "Creating desktop entry..."
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/stock-analyzer.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Stock Analyzer Pro
Comment=Professional stock market analysis tool
Exec=$(pwd)/run_stock_analyzer.sh
Icon=$(pwd)/stock_analyzer_icon.png
Terminal=false
Categories=Office;Finance;
EOF
chmod +x ~/.local/share/applications/stock-analyzer.desktop
echo
echo "Setup complete! Look for 'Stock Analyzer Pro' in your applications menu."
echo "Or run: ./run_stock_analyzer.sh"
