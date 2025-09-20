import yfinance as yf
import pandas as pd

# Test: Get Apple stock data
ticker = "AAPL"
stock = yf.Ticker(ticker)

# Get 6 months of data
data = stock.history(period="6mo")

print(f"Stock data for {ticker}:")
print(data.head())
print(f"\nTotal days of data: {len(data)}")
