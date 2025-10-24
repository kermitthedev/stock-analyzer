"""
Stock Analyzer Pro - Clean Modern Edition
A beautiful, professional stock analysis tool
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
from datetime import datetime
import json
import os

class StockAnalyzerPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Analyzer Pro")
        
        # Set window size
        window_width = 1600
        window_height = 900
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Clean modern colors
        self.colors = {
            'bg': '#1a1a2e',           # Dark background
            'sidebar': '#16213e',       # Sidebar
            'card': '#0f3460',          # Cards
            'accent': '#00adb5',        # Teal accent
            'text': '#eaeaea',          # Light text
            'text_dim': '#94a1b2',      # Dim text
            'success': '#4caf50',       # Green
            'danger': '#f44336',        # Red
            'warning': '#ff9800',       # Orange
        }
        
        root.configure(bg=self.colors['bg'])
        
        # Data
        self.watchlist_file = "watchlist.json"
        self.watchlist = self.load_watchlist()
        self.current_ticker = None
        self.chart_data = None
        
        # Build UI
        self.build_ui()
        
    def load_watchlist(self):
        """Load watchlist"""
        if os.path.exists(self.watchlist_file):
            try:
                with open(self.watchlist_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_watchlist(self):
        """Save watchlist"""
        try:
            with open(self.watchlist_file, 'w') as f:
                json.dump(self.watchlist, f)
        except:
            pass
    
    def build_ui(self):
        """Build the user interface"""
        # Top bar
        top_bar = tk.Frame(self.root, bg=self.colors['sidebar'], height=70)
        top_bar.pack(side=tk.TOP, fill=tk.X)
        top_bar.pack_propagate(False)
        
        # Logo
        logo = tk.Label(top_bar, text="📊 Stock Analyzer Pro", 
                       font=('Arial', 18, 'bold'),
                       fg=self.colors['accent'], bg=self.colors['sidebar'])
        logo.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Search area
        search_frame = tk.Frame(top_bar, bg=self.colors['card'])
        search_frame.pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Label(search_frame, text="Ticker:", font=('Arial', 10),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT, padx=(10,5))
        
        self.ticker_entry = tk.Entry(search_frame, font=('Arial', 11), width=10,
                                     bg=self.colors['sidebar'], fg=self.colors['text'],
                                     insertbackground=self.colors['accent'], bd=0)
        self.ticker_entry.pack(side=tk.LEFT, padx=5, pady=8)
        self.ticker_entry.bind('<Return>', lambda e: self.analyze())
        
        tk.Label(search_frame, text="Period:", font=('Arial', 10),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT, padx=(15,5))
        
        self.period_var = tk.StringVar(value="1y")
        period_combo = ttk.Combobox(search_frame, textvariable=self.period_var,
                                    values=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
                                    width=8, state='readonly', font=('Arial', 10))
        period_combo.pack(side=tk.LEFT, padx=5, pady=8)
        
        # Analyze button
        analyze_btn = tk.Button(search_frame, text="ANALYZE", command=self.analyze,
                               font=('Arial', 10, 'bold'), bg=self.colors['accent'],
                               fg='white', bd=0, padx=20, pady=8, cursor='hand2')
        analyze_btn.pack(side=tk.LEFT, padx=10)
        
        # Export button
        export_btn = tk.Button(top_bar, text="💾 Export", command=self.export_chart,
                              font=('Arial', 10), bg=self.colors['success'],
                              fg='white', bd=0, padx=15, pady=8, cursor='hand2')
        export_btn.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # Watchlist button
        watchlist_btn = tk.Button(top_bar, text="⭐ Watchlist", command=self.show_watchlist,
                                 font=('Arial', 10), bg=self.colors['warning'],
                                 fg='white', bd=0, padx=15, pady=8, cursor='hand2')
        watchlist_btn.pack(side=tk.RIGHT, padx=10, pady=15)
        
        # Main content
        main = tk.Frame(self.root, bg=self.colors['bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Info
        left = tk.Frame(main, bg=self.colors['sidebar'], width=350)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
        left.pack_propagate(False)
        
        # Stock info
        info_label = tk.Label(left, text="📈 Stock Information", 
                             font=('Arial', 12, 'bold'),
                             fg=self.colors['text'], bg=self.colors['sidebar'])
        info_label.pack(pady=(20,10), padx=20, anchor=tk.W)
        
        self.info_text = tk.Text(left, bg=self.colors['card'], fg=self.colors['text'],
                                font=('Courier', 9), bd=0, wrap=tk.WORD, height=12)
        self.info_text.pack(fill=tk.X, padx=20, pady=(0,20))
        
        # Signals
        signals_label = tk.Label(left, text="🎯 Trading Signals", 
                                font=('Arial', 12, 'bold'),
                                fg=self.colors['text'], bg=self.colors['sidebar'])
        signals_label.pack(pady=(10,10), padx=20, anchor=tk.W)
        
        self.signals_text = tk.Text(left, bg=self.colors['card'], fg=self.colors['text'],
                                   font=('Courier', 9), bd=0, wrap=tk.WORD, height=15)
        self.signals_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0,20))
        
        # Right panel - Chart
        right = tk.Frame(main, bg=self.colors['card'])
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Chart header
        chart_header = tk.Frame(right, bg=self.colors['card'], height=50)
        chart_header.pack(fill=tk.X)
        chart_header.pack_propagate(False)
        
        self.chart_title = tk.Label(chart_header, text="Select a stock to begin", 
                                    font=('Arial', 14, 'bold'),
                                    fg=self.colors['text'], bg=self.colors['card'])
        self.chart_title.pack(side=tk.LEFT, pady=15, padx=20)
        
        self.add_watchlist_btn = tk.Button(chart_header, text="⭐ Add to Watchlist",
                                          command=self.add_to_watchlist,
                                          font=('Arial', 9), bg=self.colors['warning'],
                                          fg='white', bd=0, padx=15, pady=6,
                                          cursor='hand2', state='disabled')
        self.add_watchlist_btn.pack(side=tk.RIGHT, pady=15, padx=20)
        
        # Chart area
        self.chart_frame = tk.Frame(right, bg=self.colors['bg'])
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0,20))
        
        # Welcome message
        self.show_welcome()
        
        # Status bar
        status = tk.Frame(self.root, bg=self.colors['sidebar'], height=30)
        status.pack(side=tk.BOTTOM, fill=tk.X)
        status.pack_propagate(False)
        
        self.status_label = tk.Label(status, text="Ready", 
                                     font=('Arial', 9),
                                     fg=self.colors['text_dim'], bg=self.colors['sidebar'])
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        self.progress = ttk.Progressbar(status, mode='indeterminate', length=150)
    
    def show_welcome(self):
        """Show welcome message"""
        welcome = tk.Frame(self.chart_frame, bg=self.colors['bg'])
        welcome.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        icon = tk.Label(welcome, text="📊", font=('Arial', 60),
                       fg=self.colors['accent'], bg=self.colors['bg'])
        icon.pack()
        
        title = tk.Label(welcome, text="Stock Analyzer Pro",
                        font=('Arial', 20, 'bold'),
                        fg=self.colors['text'], bg=self.colors['bg'])
        title.pack(pady=20)
        
        subtitle = tk.Label(welcome, text="Enter a ticker symbol and click ANALYZE",
                           font=('Arial', 12),
                           fg=self.colors['text_dim'], bg=self.colors['bg'])
        subtitle.pack()
        
        # Quick stocks
        quick_frame = tk.Frame(welcome, bg=self.colors['bg'])
        quick_frame.pack(pady=30)
        
        tk.Label(quick_frame, text="Quick: ", font=('Arial', 10),
                fg=self.colors['text_dim'], bg=self.colors['bg']).pack(side=tk.LEFT)
        
        for ticker in ["AAPL", "TSLA", "GOOGL", "MSFT", "NVDA"]:
            btn = tk.Button(quick_frame, text=ticker,
                          command=lambda t=ticker: self.quick_analyze(t),
                          font=('Arial', 9, 'bold'), bg=self.colors['card'],
                          fg=self.colors['accent'], bd=0, padx=12, pady=6,
                          cursor='hand2')
            btn.pack(side=tk.LEFT, padx=5)
    
    def quick_analyze(self, ticker):
        """Quick analyze"""
        self.ticker_entry.delete(0, tk.END)
        self.ticker_entry.insert(0, ticker)
        self.analyze()
    
    def analyze(self):
        """Analyze stock"""
        ticker = self.ticker_entry.get().strip().upper()
        if not ticker:
            messagebox.showwarning("Input Required", "Please enter a ticker symbol")
            return
        
        self.current_ticker = ticker
        self.status_label.config(text=f"Analyzing {ticker}...")
        self.progress.pack(side=tk.RIGHT, padx=20)
        self.progress.start(10)
        
        # Clear
        self.info_text.delete(1.0, tk.END)
        self.signals_text.delete(1.0, tk.END)
        
        # Run in thread
        thread = threading.Thread(target=self._analyze_thread, args=(ticker,))
        thread.daemon = True
        thread.start()
    
    def _analyze_thread(self, ticker):
        """Analysis thread"""
        try:
            period = self.period_var.get()
            
            # Fetch data
            stock = yf.Ticker(ticker)
            data = stock.history(period=period)
            
            if data.empty:
                self.root.after(0, messagebox.showerror, "Error", 
                              f"No data found for {ticker}")
                return
            
            # Calculate indicators
            data = self.calculate_indicators(data)
            self.chart_data = data
            
            # Update UI
            self.root.after(0, self.create_chart, data, ticker, stock)
            self.root.after(0, self.show_analysis, data, ticker, stock)
            
            # Enable watchlist button
            if ticker not in self.watchlist:
                self.root.after(0, self.add_watchlist_btn.config,
                              {'text': '⭐ Add to Watchlist', 'state': 'normal'})
            else:
                self.root.after(0, self.add_watchlist_btn.config,
                              {'text': '✓ In Watchlist', 'state': 'disabled'})
            
            self.root.after(0, self.status_label.config, {'text': 'Ready'})
            
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", 
                          f"Analysis failed:\n{str(e)}")
            self.root.after(0, self.status_label.config, {'text': 'Error'})
        finally:
            self.root.after(0, self.progress.stop)
            self.root.after(0, self.progress.pack_forget)
    
    def calculate_indicators(self, data):
        """Calculate indicators"""
        # Moving averages
        data['MA_20'] = data['Close'].rolling(window=20).mean()
        data['MA_50'] = data['Close'].rolling(window=50).mean()
        
        # RSI
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = data['Close'].ewm(span=12, adjust=False).mean()
        ema_26 = data['Close'].ewm(span=26, adjust=False).mean()
        data['MACD'] = ema_12 - ema_26
        data['MACD_Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
        
        # Bollinger Bands
        sma = data['Close'].rolling(window=20).mean()
        std = data['Close'].rolling(window=20).std()
        data['BB_Upper'] = sma + (std * 2)
        data['BB_Lower'] = sma - (std * 2)
        
        return data
    
    def create_chart(self, data, ticker, stock):
        """Create chart"""
        # Clear previous
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        # Update title
        self.chart_title.config(text=f"{ticker} - {self.period_var.get().upper()}")
        
        # Create figure
        fig = plt.figure(figsize=(14, 9), facecolor=self.colors['bg'])
        gs = fig.add_gridspec(3, 1, height_ratios=[2, 1, 1], hspace=0.1)
        
        ax1 = fig.add_subplot(gs[0])  # Price
        ax2 = fig.add_subplot(gs[1], sharex=ax1)  # Volume
        ax3 = fig.add_subplot(gs[2], sharex=ax1)  # RSI
        
        # Style
        for ax in [ax1, ax2, ax3]:
            ax.set_facecolor(self.colors['card'])
            for spine in ax.spines.values():
                spine.set_color(self.colors['sidebar'])
            ax.tick_params(colors=self.colors['text_dim'], labelsize=9)
            ax.grid(True, alpha=0.2, color=self.colors['sidebar'])
        
        # Price chart
        ax1.plot(data.index, data['Close'], linewidth=2.5, 
                color=self.colors['accent'], label='Price')
        ax1.plot(data.index, data['MA_20'], linewidth=2, 
                color=self.colors['success'], alpha=0.8, label='MA 20')
        ax1.plot(data.index, data['MA_50'], linewidth=2,
                color=self.colors['warning'], alpha=0.8, label='MA 50')
        
        # Bollinger Bands
        ax1.fill_between(data.index, data['BB_Upper'], data['BB_Lower'],
                        alpha=0.1, color=self.colors['accent'])
        
        ax1.set_ylabel('Price ($)', color=self.colors['text'], fontsize=11, fontweight='bold')
        ax1.set_title(f'{ticker} Technical Analysis', color=self.colors['text'],
                     fontsize=14, fontweight='bold', pad=15)
        ax1.legend(loc='upper left', fontsize=9, framealpha=0.9)
        
        # Volume
        colors = [self.colors['success'] if data['Close'].iloc[i] >= data['Open'].iloc[i]
                 else self.colors['danger'] for i in range(len(data))]
        ax2.bar(data.index, data['Volume'], color=colors, alpha=0.6)
        ax2.set_ylabel('Volume', color=self.colors['text'], fontsize=10, fontweight='bold')
        
        # RSI
        ax3.plot(data.index, data['RSI'], linewidth=2, color=self.colors['accent'])
        ax3.axhline(70, color=self.colors['danger'], linestyle='--', alpha=0.5)
        ax3.axhline(30, color=self.colors['success'], linestyle='--', alpha=0.5)
        ax3.fill_between(data.index, 70, 100, alpha=0.1, color=self.colors['danger'])
        ax3.fill_between(data.index, 0, 30, alpha=0.1, color=self.colors['success'])
        ax3.set_ylabel('RSI', color=self.colors['text'], fontsize=10, fontweight='bold')
        ax3.set_ylim(0, 100)
        ax3.set_xlabel('Date', color=self.colors['text'], fontsize=10)
        
        # Hide x labels except bottom
        plt.setp(ax1.get_xticklabels(), visible=False)
        plt.setp(ax2.get_xticklabels(), visible=False)
        
        plt.tight_layout()
        
        # Embed
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.current_canvas = canvas
    
    def show_analysis(self, data, ticker, stock):
        """Show analysis"""
        current_price = data['Close'].iloc[-1]
        prev_price = data['Close'].iloc[-2]
        change = ((current_price - prev_price) / prev_price) * 100
        
        ma20 = data['MA_20'].iloc[-1]
        ma50 = data['MA_50'].iloc[-1]
        rsi = data['RSI'].iloc[-1]
        
        # Get company info
        try:
            info = stock.info
            name = info.get('longName', ticker)
            market_cap = info.get('marketCap', 0)
        except:
            name = ticker
            market_cap = 0
        
        # Stock info
        info_text = f"{ticker}\n"
        info_text += f"{'='*30}\n\n"
        info_text += f"{name}\n\n"
        
        if market_cap > 1e9:
            info_text += f"Market Cap: ${market_cap/1e9:.1f}B\n\n"
        elif market_cap > 1e6:
            info_text += f"Market Cap: ${market_cap/1e6:.1f}M\n\n"
        
        info_text += f"Price: ${current_price:.2f}\n"
        info_text += f"Change: {change:+.2f}%\n\n"
        info_text += f"MA-20: ${ma20:.2f}\n"
        info_text += f"MA-50: ${ma50:.2f}\n"
        info_text += f"RSI: {rsi:.1f}\n"
        
        self.info_text.insert(tk.END, info_text)
        
        # Signals
        signals = ""
        score = 0
        
        # MA Signal
        if pd.notna(ma20) and pd.notna(ma50):
            if ma20 > ma50:
                signals += "✓ Bullish MA Crossover\n"
                signals += "  20-MA > 50-MA\n\n"
                score += 2
            else:
                signals += "✗ Bearish MA Crossover\n"
                signals += "  20-MA < 50-MA\n\n"
                score -= 2
        
        # Price vs MA
        if current_price > ma20:
            signals += "✓ Price Above 20-MA\n\n"
            score += 1
        else:
            signals += "✗ Price Below 20-MA\n\n"
            score -= 1
        
        # RSI
        if rsi > 70:
            signals += "! Overbought (RSI > 70)\n\n"
            score -= 1
        elif rsi < 30:
            signals += "✓ Oversold (RSI < 30)\n\n"
            score += 1
        else:
            signals += "○ RSI Neutral\n\n"
        
        signals += f"Score: {score}\n"
        signals += "{'='*30}\n\n"
        
        # Recommendation
        if score >= 3:
            signals += "RECOMMENDATION:\n"
            signals += "🟢 STRONG BUY\n"
            signals += "Multiple bullish signals"
        elif score >= 1:
            signals += "RECOMMENDATION:\n"
            signals += "🟢 BUY\n"
            signals += "Positive indicators"
        elif score >= -1:
            signals += "RECOMMENDATION:\n"
            signals += "🟡 HOLD\n"
            signals += "Mixed signals"
        else:
            signals += "RECOMMENDATION:\n"
            signals += "🔴 SELL\n"
            signals += "Bearish indicators"
        
        self.signals_text.insert(tk.END, signals)
    
    def show_watchlist(self):
        """Show watchlist"""
        win = tk.Toplevel(self.root)
        win.title("Watchlist")
        win.geometry("400x500")
        win.configure(bg=self.colors['bg'])
        
        header = tk.Frame(win, bg=self.colors['sidebar'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="⭐ My Watchlist", font=('Arial', 14, 'bold'),
                fg=self.colors['text'], bg=self.colors['sidebar']).pack(pady=20, padx=20, anchor=tk.W)
        
        content = tk.Frame(win, bg=self.colors['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        if not self.watchlist:
            tk.Label(content, text="No stocks in watchlist\n\nAdd stocks to track them!",
                    font=('Arial', 11), fg=self.colors['text_dim'],
                    bg=self.colors['bg'], justify=tk.CENTER).pack(expand=True)
        else:
            for ticker in self.watchlist:
                item = tk.Frame(content, bg=self.colors['card'])
                item.pack(fill=tk.X, pady=5)
                
                tk.Label(item, text=ticker, font=('Arial', 12, 'bold'),
                        fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT, padx=15, pady=10)
                
                tk.Button(item, text="Analyze",
                         command=lambda t=ticker: self.analyze_watchlist_item(t, win),
                         font=('Arial', 9), bg=self.colors['accent'],
                         fg='white', bd=0, padx=12, pady=6,
                         cursor='hand2').pack(side=tk.RIGHT, padx=5, pady=5)
                
                tk.Button(item, text="Remove",
                         command=lambda t=ticker: self.remove_from_watchlist(t, content),
                         font=('Arial', 9), bg=self.colors['danger'],
                         fg='white', bd=0, padx=12, pady=6,
                         cursor='hand2').pack(side=tk.RIGHT, padx=5, pady=5)
    
    def analyze_watchlist_item(self, ticker, window):
        """Analyze from watchlist"""
        window.destroy()
        self.ticker_entry.delete(0, tk.END)
        self.ticker_entry.insert(0, ticker)
        self.analyze()
    
    def add_to_watchlist(self):
        """Add to watchlist"""
        if self.current_ticker and self.current_ticker not in self.watchlist:
            self.watchlist.append(self.current_ticker)
            self.save_watchlist()
            messagebox.showinfo("Success", f"{self.current_ticker} added to watchlist!")
            self.add_watchlist_btn.config(text="✓ In Watchlist", state='disabled')
    
    def remove_from_watchlist(self, ticker, parent):
        """Remove from watchlist"""
        if ticker in self.watchlist:
            self.watchlist.remove(ticker)
            self.save_watchlist()
            # Refresh display
            for widget in parent.winfo_children():
                widget.destroy()
            if self.watchlist:
                for t in self.watchlist:
                    item = tk.Frame(parent, bg=self.colors['card'])
                    item.pack(fill=tk.X, pady=5)
                    
                    tk.Label(item, text=t, font=('Arial', 12, 'bold'),
                            fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT, padx=15, pady=10)
                    
                    tk.Button(item, text="Analyze",
                             command=lambda ticker=t: self.analyze_watchlist_item(ticker, parent.master),
                             font=('Arial', 9), bg=self.colors['accent'],
                             fg='white', bd=0, padx=12, pady=6,
                             cursor='hand2').pack(side=tk.RIGHT, padx=5, pady=5)
                    
                    tk.Button(item, text="Remove",
                             command=lambda ticker=t: self.remove_from_watchlist(ticker, parent),
                             font=('Arial', 9), bg=self.colors['danger'],
                             fg='white', bd=0, padx=12, pady=6,
                             cursor='hand2').pack(side=tk.RIGHT, padx=5, pady=5)
            else:
                tk.Label(parent, text="No stocks in watchlist\n\nAdd stocks to track them!",
                        font=('Arial', 11), fg=self.colors['text_dim'],
                        bg=self.colors['bg'], justify=tk.CENTER).pack(expand=True)
    
    def export_chart(self):
        """Export chart"""
        if not hasattr(self, 'current_canvas') or not self.current_ticker:
            messagebox.showwarning("No Chart", "Analyze a stock first!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=f"{self.current_ticker}_analysis.png",
            filetypes=[("PNG", "*.png"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                self.current_canvas.figure.savefig(filename, dpi=300,
                                                   bbox_inches='tight',
                                                   facecolor=self.colors['bg'])
                messagebox.showinfo("Success", "Chart exported!")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = StockAnalyzerPro(root)
    root.mainloop()
