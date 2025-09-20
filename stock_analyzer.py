import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def calculate_rsi(prices, window=14):
    """Calculate RSI (Relative Strength Index)"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Get stock data
ticker = "AAPL"
print(f"Fetching data for {ticker}...")

stock = yf.Ticker(ticker)
data = stock.history(period="6mo")

print(f"Got {len(data)} days of data")
print(f"Price range: ${data['Close'].min():.2f} - ${data['Close'].max():.2f}")

# Calculate indicators
data['MA_20'] = data['Close'].rolling(window=20).mean()
data['MA_50'] = data['Close'].rolling(window=50).mean()
data['RSI'] = calculate_rsi(data['Close'])

# Create subplot layout
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), height_ratios=[3, 1])

# Top chart: Price and Moving Averages
ax1.plot(data.index, data['Close'], linewidth=2, label=f'{ticker} Close Price', color='blue')
ax1.plot(data.index, data['MA_20'], linewidth=1.5, label='20-day MA', color='orange')
ax1.plot(data.index, data['MA_50'], linewidth=1.5, label='50-day MA', color='red')
ax1.set_title(f'{ticker} Stock Analysis - Last 6 Months')
ax1.set_ylabel('Price ($)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Bottom chart: RSI
ax2.plot(data.index, data['RSI'], linewidth=2, label='RSI', color='purple')
ax2.axhline(y=70, color='r', linestyle='--', alpha=0.7, label='Overbought (70)')
ax2.axhline(y=30, color='g', linestyle='--', alpha=0.7, label='Oversold (30)')
ax2.fill_between(data.index, 70, 100, alpha=0.1, color='red')
ax2.fill_between(data.index, 0, 30, alpha=0.1, color='green')
ax2.set_ylabel('RSI')
ax2.set_xlabel('Date')
ax2.set_ylim(0, 100)
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'{ticker}_full_analysis.png', dpi=300, bbox_inches='tight')
print(f"Chart saved as {ticker}_full_analysis.png")

# Analysis and signals
current_price = data['Close'].iloc[-1]
current_ma20 = data['MA_20'].iloc[-1]
current_ma50 = data['MA_50'].iloc[-1]
current_rsi = data['RSI'].iloc[-1]

print(f"\n=== CURRENT ANALYSIS ===")
print(f"Current Price: ${current_price:.2f}")
print(f"20-day MA: ${current_ma20:.2f}")
print(f"50-day MA: ${current_ma50:.2f}")
print(f"RSI: {current_rsi:.1f}")

print(f"\n=== SIGNALS ===")

# Moving Average Signal
if current_ma20 > current_ma50:
    print("📈 BULLISH: 20-day MA above 50-day MA")
else:
    print("📉 BEARISH: 20-day MA below 50-day MA")

# RSI Signal
if current_rsi > 70:
    print("⚠️  OVERBOUGHT: RSI > 70 - Consider selling")
elif current_rsi < 30:
    print("🟢 OVERSOLD: RSI < 30 - Consider buying")
else:
    print(f"📊 NEUTRAL: RSI in normal range")

# Overall recommendation
if current_ma20 > current_ma50 and current_rsi < 70:
    print("\n🚀 OVERALL: BUY signal - Bullish trend, not overbought")
elif current_ma20 < current_ma50 and current_rsi > 30:
    print("\n🔻 OVERALL: SELL signal - Bearish trend, not oversold")
else:
    print("\n⏸️  OVERALL: HOLD - Mixed signals")

plt.close()
