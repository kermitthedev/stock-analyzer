"""
Stock Analyzer Pro - Premium Edition
Advanced stock analysis with modern UI and professional features
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.patches import Rectangle
import matplotlib.dates as mdates
import threading
from datetime import datetime, timedelta
import json
import os

class StockAnalyzerPremium:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Analyzer Pro - Premium Edition")
        
        # Window setup
        window_width = 1800
        window_height = 1000
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Theme settings
        self.current_theme = "dark"
        self.themes = {
            'dark': {
                'bg': '#0d1117',
                'card': '#161b22',
                'sidebar': '#1c2128',
                'accent': '#58a6ff',
                'success': '#3fb950',
                'danger': '#f85149',
                'warning': '#d29922',
                'text': '#c9d1d9',
                'text_dim': '#8b949e',
                'border': '#30363d',
                'hover': '#21262d'
            },
            'light': {
                'bg': '#ffffff',
                'card': '#f6f8fa',
                'sidebar': '#f0f2f5',
                'accent': '#0969da',
                'success': '#1a7f37',
                'danger': '#cf222e',
                'warning': '#9a6700',
                'text': '#24292f',
                'text_dim': '#57606a',
                'border': '#d0d7de',
                'hover': '#e7eaed'
            }
        }
        
        self.colors = self.themes[self.current_theme]
        
        # Data
        self.watchlist_file = "watchlist.json"
        self.watchlist = self.load_watchlist()
        self.alerts_file = "alerts.json"
        self.alerts = self.load_alerts()
        self.current_ticker = None
        self.chart_data = None
        self.current_canvas = None
        
        # Indicator settings
        self.show_ma20 = tk.BooleanVar(value=True)
        self.show_ma50 = tk.BooleanVar(value=True)
        self.show_bollinger = tk.BooleanVar(value=True)
        self.show_macd = tk.BooleanVar(value=True)
        self.chart_type = tk.StringVar(value="candlestick")
        
        # Build UI
        self.build_ui()
        
    def load_watchlist(self):
        if os.path.exists(self.watchlist_file):
            try:
                with open(self.watchlist_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_watchlist(self):
        try:
            with open(self.watchlist_file, 'w') as f:
                json.dump(self.watchlist, f)
        except:
            pass
    
    def load_alerts(self):
        if os.path.exists(self.alerts_file):
            try:
                with open(self.alerts_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_alerts(self):
        try:
            with open(self.alerts_file, 'w') as f:
                json.dump(self.alerts, f)
        except:
            pass
    
    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.colors = self.themes[self.current_theme]
        self.refresh_ui()
    
    def refresh_ui(self):
        """Refresh UI with new theme"""
        # Just rebuild everything - simpler than updating each widget
        for widget in self.root.winfo_children():
            widget.destroy()
        self.build_ui()
        if self.current_ticker and self.chart_data is not None:
            self.create_chart(self.chart_data, self.current_ticker, None)
    
    def build_ui(self):
        """Build the user interface"""
        self.root.configure(bg=self.colors['bg'])
        
        # Top bar
        top_bar = tk.Frame(self.root, bg=self.colors['card'], height=80)
        top_bar.pack(side=tk.TOP, fill=tk.X)
        top_bar.pack_propagate(False)
        
        # Logo
        logo_frame = tk.Frame(top_bar, bg=self.colors['card'])
        logo_frame.pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Label(logo_frame, text="📊 Stock Analyzer", 
                font=('Arial', 16, 'bold'),
                fg=self.colors['accent'], bg=self.colors['card']).pack()
        tk.Label(logo_frame, text="Premium Edition", 
                font=('Arial', 8),
                fg=self.colors['text_dim'], bg=self.colors['card']).pack()
        
        # Search area - Modern card style
        search_card = tk.Frame(top_bar, bg=self.colors['sidebar'], relief='flat', bd=0)
        search_card.pack(side=tk.LEFT, padx=20, pady=12)
        
        search_inner = tk.Frame(search_card, bg=self.colors['sidebar'])
        search_inner.pack(padx=15, pady=10)
        
        # Ticker
        tk.Label(search_inner, text="Ticker:", font=('Arial', 9, 'bold'),
                fg=self.colors['text'], bg=self.colors['sidebar']).grid(row=0, column=0, padx=(0,5), sticky=tk.W)
        
        self.ticker_entry = tk.Entry(search_inner, font=('Arial', 11), width=10,
                                     bg=self.colors['card'], fg=self.colors['text'],
                                     insertbackground=self.colors['accent'], bd=1,
                                     relief='solid')
        self.ticker_entry.grid(row=0, column=1, padx=5)
        self.ticker_entry.bind('<Return>', lambda e: self.analyze())
        
        # Period
        tk.Label(search_inner, text="Period:", font=('Arial', 9, 'bold'),
                fg=self.colors['text'], bg=self.colors['sidebar']).grid(row=0, column=2, padx=(15,5), sticky=tk.W)
        
        self.period_var = tk.StringVar(value="1y")
        period_combo = ttk.Combobox(search_inner, textvariable=self.period_var,
                                    values=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
                                    width=8, state='readonly', font=('Arial', 9))
        period_combo.grid(row=0, column=3, padx=5)
        
        # Chart type
        tk.Label(search_inner, text="Chart:", font=('Arial', 9, 'bold'),
                fg=self.colors['text'], bg=self.colors['sidebar']).grid(row=0, column=4, padx=(15,5), sticky=tk.W)
        
        chart_combo = ttk.Combobox(search_inner, textvariable=self.chart_type,
                                   values=["candlestick", "line"],
                                   width=10, state='readonly', font=('Arial', 9))
        chart_combo.grid(row=0, column=5, padx=5)
        
        # Analyze button
        analyze_btn = tk.Button(search_inner, text="⚡ ANALYZE", command=self.analyze,
                               font=('Arial', 10, 'bold'), bg=self.colors['accent'],
                               fg='white', bd=0, padx=20, pady=8, cursor='hand2',
                               activebackground=self.colors['accent'])
        analyze_btn.grid(row=0, column=6, padx=15)
        
        # Right side buttons
        btn_frame = tk.Frame(top_bar, bg=self.colors['card'])
        btn_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # Theme toggle
        theme_icon = "🌙" if self.current_theme == "dark" else "☀️"
        tk.Button(btn_frame, text=theme_icon, command=self.toggle_theme,
                 font=('Arial', 14), bg=self.colors['sidebar'],
                 fg=self.colors['text'], bd=0, padx=12, pady=6,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        # Indicators
        tk.Button(btn_frame, text="📊 Indicators", command=self.show_indicators,
                 font=('Arial', 9, 'bold'), bg=self.colors['sidebar'],
                 fg=self.colors['text'], bd=0, padx=12, pady=8,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        # Compare
        tk.Button(btn_frame, text="📈 Compare", command=self.compare_stocks,
                 font=('Arial', 9, 'bold'), bg=self.colors['sidebar'],
                 fg=self.colors['text'], bd=0, padx=12, pady=8,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        # Watchlist
        tk.Button(btn_frame, text="⭐ Watchlist", command=self.show_watchlist,
                 font=('Arial', 9, 'bold'), bg=self.colors['warning'],
                 fg='white', bd=0, padx=12, pady=8,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        # Export
        tk.Button(btn_frame, text="💾 Export", command=self.export_menu,
                 font=('Arial', 9, 'bold'), bg=self.colors['success'],
                 fg='white', bd=0, padx=12, pady=8,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        # Main content - Card grid layout
        main = tk.Frame(self.root, bg=self.colors['bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Left panel - Info cards
        left = tk.Frame(main, bg=self.colors['bg'], width=380)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0,15))
        left.pack_propagate(False)
        
        # Stock Info Card
        info_card = self.create_card(left, "📈 Stock Information")
        self.info_text = tk.Text(info_card, bg=self.colors['card'], 
                                fg=self.colors['text'],
                                font=('Courier', 9), bd=0, wrap=tk.WORD, 
                                height=12, relief='flat')
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0,15))
        
        # Trading Signals Card
        signals_card = self.create_card(left, "🎯 Trading Signals")
        self.signals_text = tk.Text(signals_card, bg=self.colors['card'],
                                   fg=self.colors['text'],
                                   font=('Courier', 9), bd=0, wrap=tk.WORD,
                                   height=18, relief='flat')
        self.signals_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0,15))
        
        # Recommendation Card
        rec_card = self.create_card(left, "💡 AI Recommendation")
        self.rec_frame = tk.Frame(rec_card, bg=self.colors['card'])
        self.rec_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0,15))
        
        tk.Label(self.rec_frame, text="Analyze a stock to see AI-powered insights",
                font=('Arial', 10), fg=self.colors['text_dim'],
                bg=self.colors['card'], wraplength=330).pack(pady=30)
        
        # Right panel - Chart
        right = tk.Frame(main, bg=self.colors['bg'])
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Chart card
        chart_card = tk.Frame(right, bg=self.colors['card'], relief='flat', bd=0)
        chart_card.pack(fill=tk.BOTH, expand=True)
        
        # Chart header
        chart_header = tk.Frame(chart_card, bg=self.colors['card'], height=55)
        chart_header.pack(fill=tk.X)
        chart_header.pack_propagate(False)
        
        header_left = tk.Frame(chart_header, bg=self.colors['card'])
        header_left.pack(side=tk.LEFT, pady=12, padx=20)
        
        self.chart_title = tk.Label(header_left, text="Select a stock to begin", 
                                    font=('Arial', 13, 'bold'),
                                    fg=self.colors['text'], bg=self.colors['card'])
        self.chart_title.pack(side=tk.LEFT)
        
        self.price_label = tk.Label(header_left, text="", 
                                    font=('Arial', 11),
                                    fg=self.colors['text_dim'], bg=self.colors['card'])
        self.price_label.pack(side=tk.LEFT, padx=15)
        
        # Header buttons
        header_right = tk.Frame(chart_header, bg=self.colors['card'])
        header_right.pack(side=tk.RIGHT, pady=12, padx=20)
        
        self.add_watchlist_btn = tk.Button(header_right, text="⭐ Add to Watchlist",
                                          command=self.add_to_watchlist,
                                          font=('Arial', 9), bg=self.colors['warning'],
                                          fg='white', bd=0, padx=12, pady=6,
                                          cursor='hand2', state='disabled')
        self.add_watchlist_btn.pack(side=tk.LEFT, padx=5)
        
        self.alert_btn = tk.Button(header_right, text="🔔 Set Alert",
                                   command=self.set_alert,
                                   font=('Arial', 9), bg=self.colors['accent'],
                                   fg='white', bd=0, padx=12, pady=6,
                                   cursor='hand2', state='disabled')
        self.alert_btn.pack(side=tk.LEFT, padx=5)
        
        # Separator
        tk.Frame(chart_card, bg=self.colors['border'], height=1).pack(fill=tk.X)
        
        # Chart area
        self.chart_frame = tk.Frame(chart_card, bg=self.colors['card'])
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Welcome message
        self.show_welcome()
        
        # Status bar
        status = tk.Frame(self.root, bg=self.colors['card'], height=35)
        status.pack(side=tk.BOTTOM, fill=tk.X)
        status.pack_propagate(False)
        
        tk.Frame(status, bg=self.colors['border'], height=1).pack(side=tk.TOP, fill=tk.X)
        
        self.status_label = tk.Label(status, text="Ready • Premium Edition", 
                                     font=('Arial', 9),
                                     fg=self.colors['text_dim'], bg=self.colors['card'])
        self.status_label.pack(side=tk.LEFT, padx=20, pady=8)
        
        self.progress = ttk.Progressbar(status, mode='indeterminate', length=150)
    
    def create_card(self, parent, title):
        """Create a modern card with shadow effect"""
        # Card container
        card_outer = tk.Frame(parent, bg=self.colors['bg'])
        card_outer.pack(fill=tk.X, pady=(0, 15))
        
        # Card with border
        card = tk.Frame(card_outer, bg=self.colors['card'], 
                       relief='flat', bd=0,
                       highlightbackground=self.colors['border'],
                       highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = tk.Frame(card, bg=self.colors['card'], height=45)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text=title, font=('Arial', 11, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT, 
                                                                      padx=15, pady=12)
        
        # Separator
        tk.Frame(card, bg=self.colors['border'], height=1).pack(fill=tk.X)
        
        return card
    
    def show_welcome(self):
        """Show welcome screen"""
        welcome = tk.Frame(self.chart_frame, bg=self.colors['card'])
        welcome.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(welcome, text="📊", font=('Arial', 70),
                fg=self.colors['accent'], bg=self.colors['card']).pack()
        
        tk.Label(welcome, text="Professional Stock Analysis",
                font=('Arial', 22, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack(pady=15)
        
        tk.Label(welcome, text="Enter a ticker symbol and click ANALYZE\nInteractive charts • AI insights • Real-time data",
                font=('Arial', 11),
                fg=self.colors['text_dim'], bg=self.colors['card'],
                justify=tk.CENTER).pack(pady=10)
        
        # Popular stocks
        quick_frame = tk.Frame(welcome, bg=self.colors['card'])
        quick_frame.pack(pady=25)
        
        tk.Label(quick_frame, text="Popular: ", font=('Arial', 10),
                fg=self.colors['text_dim'], bg=self.colors['card']).pack(side=tk.LEFT, padx=5)
        
        for ticker in ["AAPL", "TSLA", "GOOGL", "MSFT", "NVDA", "AMZN"]:
            btn = tk.Button(quick_frame, text=ticker,
                          command=lambda t=ticker: self.quick_analyze(t),
                          font=('Arial', 9, 'bold'), 
                          bg=self.colors['sidebar'],
                          fg=self.colors['accent'], bd=0, padx=14, pady=7,
                          cursor='hand2',
                          activebackground=self.colors['hover'])
            btn.pack(side=tk.LEFT, padx=4)
    
    def quick_analyze(self, ticker):
        """Quick analyze from button"""
        self.ticker_entry.delete(0, tk.END)
        self.ticker_entry.insert(0, ticker)
        self.analyze()
    
    def show_indicators(self):
        """Show indicator settings"""
        win = tk.Toplevel(self.root)
        win.title("Indicator Settings")
        win.geometry("350x300")
        win.configure(bg=self.colors['bg'])
        win.resizable(False, False)
        
        # Header
        header = tk.Frame(win, bg=self.colors['card'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="📊 Select Indicators", font=('Arial', 13, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack(pady=20, padx=20, anchor=tk.W)
        
        tk.Frame(header, bg=self.colors['border'], height=1).pack(side=tk.BOTTOM, fill=tk.X)
        
        # Content
        content = tk.Frame(win, bg=self.colors['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        tk.Checkbutton(content, text="Moving Average (20)", variable=self.show_ma20,
                      font=('Arial', 10), bg=self.colors['bg'], fg=self.colors['text'],
                      selectcolor=self.colors['card'], activebackground=self.colors['bg'],
                      activeforeground=self.colors['text']).pack(anchor=tk.W, pady=8)
        
        tk.Checkbutton(content, text="Moving Average (50)", variable=self.show_ma50,
                      font=('Arial', 10), bg=self.colors['bg'], fg=self.colors['text'],
                      selectcolor=self.colors['card'], activebackground=self.colors['bg'],
                      activeforeground=self.colors['text']).pack(anchor=tk.W, pady=8)
        
        tk.Checkbutton(content, text="Bollinger Bands", variable=self.show_bollinger,
                      font=('Arial', 10), bg=self.colors['bg'], fg=self.colors['text'],
                      selectcolor=self.colors['card'], activebackground=self.colors['bg'],
                      activeforeground=self.colors['text']).pack(anchor=tk.W, pady=8)
        
        tk.Checkbutton(content, text="MACD", variable=self.show_macd,
                      font=('Arial', 10), bg=self.colors['bg'], fg=self.colors['text'],
                      selectcolor=self.colors['card'], activebackground=self.colors['bg'],
                      activeforeground=self.colors['text']).pack(anchor=tk.W, pady=8)
        
        # Apply button
        tk.Button(content, text="Apply & Refresh", 
                 command=lambda: [self.refresh_chart(), win.destroy()],
                 font=('Arial', 10, 'bold'), bg=self.colors['accent'],
                 fg='white', bd=0, padx=20, pady=10,
                 cursor='hand2').pack(pady=20)
    
    def refresh_chart(self):
        """Refresh chart with new settings"""
        if self.current_ticker and self.chart_data is not None:
            self.create_chart(self.chart_data, self.current_ticker, None)
    
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
            
            # Enable buttons
            if ticker not in self.watchlist:
                self.root.after(0, self.add_watchlist_btn.config,
                              {'text': '⭐ Add to Watchlist', 'state': 'normal'})
            else:
                self.root.after(0, self.add_watchlist_btn.config,
                              {'text': '✓ In Watchlist', 'state': 'disabled'})
            
            self.root.after(0, self.alert_btn.config, {'state': 'normal'})
            
            self.root.after(0, self.status_label.config, 
                          {'text': f'Analysis complete • {ticker}'})
            
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", 
                          f"Analysis failed:\n{str(e)}")
            self.root.after(0, self.status_label.config, {'text': 'Error'})
        finally:
            self.root.after(0, self.progress.stop)
            self.root.after(0, self.progress.pack_forget)
    
    def calculate_indicators(self, data):
        """Calculate technical indicators"""
        # Moving averages
        data['MA_20'] = data['Close'].rolling(window=20).mean()
        data['MA_50'] = data['Close'].rolling(window=50).mean()
        data['MA_200'] = data['Close'].rolling(window=200).mean()
        
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
        data['MACD_Hist'] = data['MACD'] - data['MACD_Signal']
        
        # Bollinger Bands
        sma = data['Close'].rolling(window=20).mean()
        std = data['Close'].rolling(window=20).std()
        data['BB_Upper'] = sma + (std * 2)
        data['BB_Lower'] = sma - (std * 2)
        
        # Volume MA
        data['Volume_MA'] = data['Volume'].rolling(window=20).mean()
        
        return data
    
    def create_chart(self, data, ticker, stock):
        """Create interactive chart with candlesticks"""
        # Clear previous
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        # Update title
        current_price = data['Close'].iloc[-1]
        prev_price = data['Close'].iloc[-2]
        change = ((current_price - prev_price) / prev_price) * 100
        change_color = self.colors['success'] if change >= 0 else self.colors['danger']
        
        self.chart_title.config(text=f"{ticker} • {self.period_var.get().upper()}")
        self.price_label.config(
            text=f"${current_price:.2f} ({change:+.2f}%)",
            fg=change_color
        )
        
        # Create figure
        fig = plt.figure(figsize=(15, 10), facecolor=self.colors['card'])
        
        # Grid layout based on indicators
        ratios = [3, 1, 1] if self.show_macd.get() else [3, 1]
        gs = fig.add_gridspec(len(ratios), 1, height_ratios=ratios, hspace=0.05)
        
        ax_idx = 0
        ax1 = fig.add_subplot(gs[ax_idx])  # Price
        ax_idx += 1
        ax2 = fig.add_subplot(gs[ax_idx], sharex=ax1)  # Volume
        ax_idx += 1
        
        axes = [ax1, ax2]
        
        if self.show_macd.get():
            ax3 = fig.add_subplot(gs[ax_idx], sharex=ax1)  # MACD
            axes.append(ax3)
        
        # Style all axes
        for ax in axes:
            ax.set_facecolor(self.colors['card'])
            for spine in ax.spines.values():
                spine.set_color(self.colors['border'])
            ax.tick_params(colors=self.colors['text_dim'], labelsize=9)
            ax.grid(True, alpha=0.2, color=self.colors['border'], linestyle='-')
        
        # PRICE CHART
        if self.chart_type.get() == "candlestick":
            self.plot_candlesticks(ax1, data)
        else:
            ax1.plot(data.index, data['Close'], linewidth=2.5,
                    color=self.colors['accent'], label='Close', zorder=5)
        
        # Moving averages
        if self.show_ma20.get():
            ax1.plot(data.index, data['MA_20'], linewidth=2,
                    label='MA 20', color=self.colors['success'], alpha=0.8, zorder=4)
        
        if self.show_ma50.get():
            ax1.plot(data.index, data['MA_50'], linewidth=2,
                    label='MA 50', color=self.colors['warning'], alpha=0.8, zorder=4)
        
        # Bollinger Bands
        if self.show_bollinger.get():
            ax1.fill_between(data.index, data['BB_Upper'], data['BB_Lower'],
                            alpha=0.1, color=self.colors['accent'], zorder=1)
            ax1.plot(data.index, data['BB_Upper'], linewidth=1,
                    color=self.colors['accent'], alpha=0.3, linestyle='--', zorder=2)
            ax1.plot(data.index, data['BB_Lower'], linewidth=1,
                    color=self.colors['accent'], alpha=0.3, linestyle='--', zorder=2)
        
        ax1.set_ylabel('Price ($)', color=self.colors['text'], fontsize=11, fontweight='bold')
        ax1.set_title(f'{ticker} Technical Analysis', color=self.colors['text'],
                     fontsize=13, fontweight='bold', pad=15)
        ax1.legend(loc='upper left', fontsize=9, framealpha=0.9,
                  facecolor=self.colors['card'], edgecolor=self.colors['border'])
        
        # VOLUME
        colors = [self.colors['success'] if data['Close'].iloc[i] >= data['Open'].iloc[i]
                 else self.colors['danger'] for i in range(len(data))]
        ax2.bar(data.index, data['Volume'], color=colors, alpha=0.6, width=0.8)
        ax2.plot(data.index, data['Volume_MA'], linewidth=2,
                color=self.colors['warning'], label='Volume MA', alpha=0.8)
        ax2.set_ylabel('Volume', color=self.colors['text'], fontsize=10, fontweight='bold')
        ax2.legend(loc='upper left', fontsize=9, framealpha=0.9,
                  facecolor=self.colors['card'], edgecolor=self.colors['border'])
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(
            lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.0f}K'))
        
        # MACD (if enabled)
        if self.show_macd.get():
            ax3.plot(data.index, data['MACD'], linewidth=2,
                    color=self.colors['accent'], label='MACD')
            ax3.plot(data.index, data['MACD_Signal'], linewidth=2,
                    color=self.colors['warning'], label='Signal')
            
            macd_colors = [self.colors['success'] if val >= 0 else self.colors['danger']
                          for val in data['MACD_Hist']]
            ax3.bar(data.index, data['MACD_Hist'], color=macd_colors, alpha=0.5, width=0.8)
            ax3.axhline(0, color=self.colors['border'], linewidth=1)
            
            ax3.set_ylabel('MACD', color=self.colors['text'], fontsize=10, fontweight='bold')
            ax3.set_xlabel('Date', color=self.colors['text'], fontsize=10)
            ax3.legend(loc='upper left', fontsize=9, framealpha=0.9,
                      facecolor=self.colors['card'], edgecolor=self.colors['border'])
        else:
            ax2.set_xlabel('Date', color=self.colors['text'], fontsize=10)
        
        # Hide x labels except bottom
        for ax in axes[:-1]:
            plt.setp(ax.get_xticklabels(), visible=False)
        
        plt.tight_layout()
        
        # Embed with toolbar (for zoom/pan)
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        
        # Toolbar
        toolbar = NavigationToolbar2Tk(canvas, self.chart_frame)
        toolbar.update()
        toolbar.config(bg=self.colors['sidebar'])
        for child in toolbar.winfo_children():
            if isinstance(child, tk.Button):
                child.config(bg=self.colors['sidebar'], fg=self.colors['text'])
        
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.current_canvas = canvas
    
    def plot_candlesticks(self, ax, data):
        """Plot candlestick chart"""
        width = 0.6
        width2 = 0.05
        
        for idx in range(len(data)):
            date = mdates.date2num(data.index[idx])
            open_price = data['Open'].iloc[idx]
            close_price = data['Close'].iloc[idx]
            high = data['High'].iloc[idx]
            low = data['Low'].iloc[idx]
            
            color = self.colors['success'] if close_price >= open_price else self.colors['danger']
            
            # Wick
            ax.plot([date, date], [low, high], color=color, linewidth=1, alpha=0.8, zorder=3)
            
            # Body
            height = abs(close_price - open_price)
            if height < 0.001:
                height = 0.001
            bottom = min(open_price, close_price)
            
            rect = Rectangle((date - width/2, bottom), width, height,
                           facecolor=color, edgecolor=color, alpha=0.9, zorder=3)
            ax.add_patch(rect)
    
    def show_analysis(self, data, ticker, stock):
        """Show detailed analysis with AI insights"""
        current_price = data['Close'].iloc[-1]
        prev_price = data['Close'].iloc[-2]
        change = ((current_price - prev_price) / prev_price) * 100
        
        ma20 = data['MA_20'].iloc[-1]
        ma50 = data['MA_50'].iloc[-1]
        ma200 = data['MA_200'].iloc[-1] if pd.notna(data['MA_200'].iloc[-1]) else None
        rsi = data['RSI'].iloc[-1]
        macd = data['MACD'].iloc[-1]
        macd_signal = data['MACD_Signal'].iloc[-1]
        
        # Get company info
        try:
            info = stock.info
            name = info.get('longName', ticker)
            market_cap = info.get('marketCap', 0)
            sector = info.get('sector', 'N/A')
            pe_ratio = info.get('trailingPE', 0)
        except:
            name = ticker
            market_cap = 0
            sector = 'N/A'
            pe_ratio = 0
        
        # Stock info with color coding
        info_text = f"{'='*40}\n"
        info_text += f"{ticker} - {name}\n"
        info_text += f"{'='*40}\n\n"
        
        info_text += f"Sector: {sector}\n"
        
        if market_cap > 1e9:
            info_text += f"Market Cap: ${market_cap/1e9:.1f}B\n"
        elif market_cap > 1e6:
            info_text += f"Market Cap: ${market_cap/1e6:.1f}M\n"
        
        if pe_ratio:
            info_text += f"P/E Ratio: {pe_ratio:.2f}\n"
        
        info_text += f"\nCurrent Price: ${current_price:.2f}\n"
        info_text += f"Change: {change:+.2f}%\n\n"
        
        info_text += f"MA-20:  ${ma20:.2f}\n"
        info_text += f"MA-50:  ${ma50:.2f}\n"
        if ma200:
            info_text += f"MA-200: ${ma200:.2f}\n"
        info_text += f"\nRSI:    {rsi:.1f}\n"
        info_text += f"MACD:   {macd:.3f}\n"
        info_text += f"Signal: {macd_signal:.3f}\n"
        
        self.info_text.insert(tk.END, info_text)
        
        # Trading signals with detailed analysis
        signals = ""
        score = 0
        insights = []
        
        # MA Analysis
        signals += "MOVING AVERAGES\n"
        signals += f"{'-'*40}\n"
        
        if pd.notna(ma20) and pd.notna(ma50):
            if ma20 > ma50:
                signals += "🟢 Bullish MA Crossover\n"
                signals += f"   20-MA (${ma20:.2f}) > 50-MA (${ma50:.2f})\n"
                insights.append("Golden cross detected - bullish momentum")
                score += 2
            else:
                signals += "🔴 Bearish MA Crossover\n"
                signals += f"   20-MA (${ma20:.2f}) < 50-MA (${ma50:.2f})\n"
                insights.append("Death cross present - bearish trend")
                score -= 2
        
        # Price vs MA
        if current_price > ma20:
            signals += "🟢 Price Above 20-MA\n"
            pct_above = ((current_price - ma20) / ma20) * 100
            signals += f"   {pct_above:.1f}% above MA\n"
            score += 1
        else:
            signals += "🔴 Price Below 20-MA\n"
            pct_below = ((ma20 - current_price) / ma20) * 100
            signals += f"   {pct_below:.1f}% below MA\n"
            score -= 1
        
        signals += "\n"
        
        # RSI Analysis
        signals += "RSI MOMENTUM\n"
        signals += f"{'-'*40}\n"
        
        if rsi > 70:
            signals += "🔴 Overbought Territory\n"
            signals += f"   RSI = {rsi:.1f} (> 70)\n"
            insights.append("Overbought - possible pullback ahead")
            score -= 1
        elif rsi < 30:
            signals += "🟢 Oversold Territory\n"
            signals += f"   RSI = {rsi:.1f} (< 30)\n"
            insights.append("Oversold - potential bounce opportunity")
            score += 2
        else:
            signals += "⚪ Neutral Zone\n"
            signals += f"   RSI = {rsi:.1f} (30-70)\n"
            if rsi > 60:
                insights.append("RSI trending toward overbought")
            elif rsi < 40:
                insights.append("RSI leaning toward oversold")
        
        signals += "\n"
        
        # MACD Analysis
        signals += "MACD SIGNAL\n"
        signals += f"{'-'*40}\n"
        
        if macd > macd_signal:
            signals += "🟢 Bullish MACD\n"
            signals += "   MACD > Signal Line\n"
            if data['MACD_Hist'].iloc[-1] > data['MACD_Hist'].iloc[-2]:
                signals += "   📈 Momentum increasing\n"
                insights.append("MACD shows strengthening uptrend")
            score += 2
        else:
            signals += "🔴 Bearish MACD\n"
            signals += "   MACD < Signal Line\n"
            if data['MACD_Hist'].iloc[-1] < data['MACD_Hist'].iloc[-2]:
                signals += "   📉 Momentum weakening\n"
                insights.append("MACD signals downward pressure")
            score -= 2
        
        signals += "\n"
        
        # Volume analysis
        signals += "VOLUME TREND\n"
        signals += f"{'-'*40}\n"
        current_vol = data['Volume'].iloc[-1]
        avg_vol = data['Volume_MA'].iloc[-1]
        
        if current_vol > avg_vol * 1.5:
            signals += "🟢 High Volume\n"
            signals += f"   {(current_vol/avg_vol):.1f}x above average\n"
            insights.append("Strong volume confirms price action")
            score += 1
        elif current_vol < avg_vol * 0.5:
            signals += "⚪ Low Volume\n"
            signals += f"   {(avg_vol/current_vol):.1f}x below average\n"
            insights.append("Weak volume - trend may lack conviction")
        else:
            signals += "⚪ Normal Volume\n"
        
        signals += "\n"
        signals += f"{'='*40}\n"
        signals += f"COMPOSITE SCORE: {score}\n"
        signals += f"{'='*40}\n"
        
        self.signals_text.insert(tk.END, signals)
        
        # AI-powered recommendation
        for widget in self.rec_frame.winfo_children():
            widget.destroy()
        
        rec_inner = tk.Frame(self.rec_frame, bg=self.colors['card'])
        rec_inner.pack(fill=tk.BOTH, expand=True, pady=15)
        
        # Recommendation based on score
        if score >= 5:
            rec = "🚀 STRONG BUY"
            rec_color = self.colors['success']
            probability = "High probability of upward movement"
            desc = "Multiple strong bullish indicators aligned. " + " ".join(insights[:2])
        elif score >= 2:
            rec = "📈 BUY"
            rec_color = self.colors['success']
            probability = "Favorable risk/reward ratio"
            desc = "Positive momentum detected. " + " ".join(insights[:2])
        elif score >= -1:
            rec = "⚪ HOLD"
            rec_color = self.colors['warning']
            probability = "Mixed signals - wait for clarity"
            desc = "Conflicting indicators suggest neutral stance. Monitor for breakout."
        elif score >= -4:
            rec = "📉 SELL"
            rec_color = self.colors['danger']
            probability = "Bearish pressure building"
            desc = "Negative indicators dominating. " + " ".join(insights[:2])
        else:
            rec = "🔻 STRONG SELL"
            rec_color = self.colors['danger']
            probability = "High risk of further decline"
            desc = "Multiple bearish signals present. " + " ".join(insights[:2])
        
        # Display recommendation
        tk.Label(rec_inner, text=rec, font=('Arial', 18, 'bold'),
                fg=rec_color, bg=self.colors['card']).pack(pady=(0,10))
        
        tk.Label(rec_inner, text=probability, font=('Arial', 10),
                fg=self.colors['text'], bg=self.colors['card']).pack()
        
        # Separator
        tk.Frame(rec_inner, bg=self.colors['border'], height=1).pack(fill=tk.X, pady=15, padx=20)
        
        # AI Summary
        tk.Label(rec_inner, text="💡 AI INSIGHT", font=('Arial', 9, 'bold'),
                fg=self.colors['text_dim'], bg=self.colors['card']).pack()
        
        tk.Label(rec_inner, text=desc, font=('Arial', 9),
                fg=self.colors['text'], bg=self.colors['card'],
                wraplength=320, justify=tk.LEFT).pack(pady=(10,0), padx=20)
    
    def compare_stocks(self):
        """Compare multiple stocks"""
        win = tk.Toplevel(self.root)
        win.title("Compare Stocks")
        win.geometry("500x400")
        win.configure(bg=self.colors['bg'])
        
        # Header
        header = tk.Frame(win, bg=self.colors['card'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="📈 Compare Stocks", font=('Arial', 13, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack(pady=20, padx=20, anchor=tk.W)
        
        tk.Frame(header, bg=self.colors['border'], height=1).pack(side=tk.BOTTOM, fill=tk.X)
        
        # Content
        content = tk.Frame(win, bg=self.colors['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        tk.Label(content, text="Enter tickers separated by commas:",
                font=('Arial', 10), fg=self.colors['text'],
                bg=self.colors['bg']).pack(anchor=tk.W, pady=(0,10))
        
        tickers_entry = tk.Entry(content, font=('Arial', 11),
                                bg=self.colors['card'], fg=self.colors['text'],
                                insertbackground=self.colors['accent'], bd=1, relief='solid')
        tickers_entry.pack(fill=tk.X, pady=(0,20))
        tickers_entry.insert(0, "AAPL, MSFT, GOOGL")
        
        tk.Button(content, text="Compare Performance",
                 command=lambda: self.do_comparison(tickers_entry.get(), win),
                 font=('Arial', 10, 'bold'), bg=self.colors['accent'],
                 fg='white', bd=0, padx=20, pady=10,
                 cursor='hand2').pack(pady=10)
        
        tk.Label(content, text="Feature coming soon: Side-by-side comparison\nof technical indicators and returns",
                font=('Arial', 9), fg=self.colors['text_dim'],
                bg=self.colors['bg'], justify=tk.CENTER).pack(pady=30)
    
    def do_comparison(self, tickers_str, window):
        """Perform stock comparison"""
        messagebox.showinfo("Coming Soon", 
                          "Multi-stock comparison feature\nwill be available in the next update!")
        window.destroy()
    
    def show_watchlist(self):
        """Show watchlist with enhanced UI"""
        win = tk.Toplevel(self.root)
        win.title("Watchlist")
        win.geometry("500x600")
        win.configure(bg=self.colors['bg'])
        
        # Header
        header = tk.Frame(win, bg=self.colors['card'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="⭐ My Watchlist", font=('Arial', 14, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT, 
                                                                      pady=25, padx=25)
        
        tk.Button(header, text="+ Add Stock",
                 command=lambda: self.quick_add_to_watchlist(win),
                 font=('Arial', 9, 'bold'), bg=self.colors['accent'],
                 fg='white', bd=0, padx=15, pady=8,
                 cursor='hand2').pack(side=tk.RIGHT, padx=25, pady=20)
        
        tk.Frame(header, bg=self.colors['border'], height=1).pack(side=tk.BOTTOM, fill=tk.X)
        
        # Content with scrollbar
        content_frame = tk.Frame(win, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(content_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable_frame.bind("<Configure>",
                             lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y", pady=20)
        
        if not self.watchlist:
            tk.Label(scrollable_frame, 
                    text="No stocks in watchlist\n\nClick '+ Add Stock' to get started",
                    font=('Arial', 11), fg=self.colors['text_dim'],
                    bg=self.colors['bg'], justify=tk.CENTER).pack(expand=True, pady=50)
        else:
            for ticker in self.watchlist:
                self.create_watchlist_card(scrollable_frame, ticker, win)
    
    def create_watchlist_card(self, parent, ticker, window):
        """Create a card for watchlist item"""
        card = tk.Frame(parent, bg=self.colors['card'],
                       highlightbackground=self.colors['border'],
                       highlightthickness=1)
        card.pack(fill=tk.X, pady=5)
        
        inner = tk.Frame(card, bg=self.colors['card'])
        inner.pack(fill=tk.X, padx=20, pady=15)
        
        # Ticker
        tk.Label(inner, text=ticker, font=('Arial', 13, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        # Buttons
        btn_frame = tk.Frame(inner, bg=self.colors['card'])
        btn_frame.pack(side=tk.RIGHT)
        
        tk.Button(btn_frame, text="Analyze",
                 command=lambda: [window.destroy(), self.quick_analyze(ticker)],
                 font=('Arial', 9), bg=self.colors['accent'],
                 fg='white', bd=0, padx=12, pady=6,
                 cursor='hand2').pack(side=tk.LEFT, padx=3)
        
        tk.Button(btn_frame, text="Remove",
                 command=lambda: self.remove_from_watchlist_ui(ticker, card),
                 font=('Arial', 9), bg=self.colors['danger'],
                 fg='white', bd=0, padx=12, pady=6,
                 cursor='hand2').pack(side=tk.LEFT, padx=3)
    
    def quick_add_to_watchlist(self, parent_win):
        """Quick add to watchlist"""
        dialog = tk.Toplevel(parent_win)
        dialog.title("Add to Watchlist")
        dialog.geometry("300x150")
        dialog.configure(bg=self.colors['bg'])
        dialog.resizable(False, False)
        
        tk.Label(dialog, text="Enter ticker symbol:",
                font=('Arial', 10), fg=self.colors['text'],
                bg=self.colors['bg']).pack(pady=(20,10))
        
        entry = tk.Entry(dialog, font=('Arial', 11), width=15,
                        bg=self.colors['card'], fg=self.colors['text'],
                        insertbackground=self.colors['accent'], bd=1, relief='solid')
        entry.pack(pady=10)
        entry.focus()
        
        def add_it():
            ticker = entry.get().strip().upper()
            if ticker and ticker not in self.watchlist:
                self.watchlist.append(ticker)
                self.save_watchlist()
                dialog.destroy()
                parent_win.destroy()
                self.show_watchlist()
            elif ticker in self.watchlist:
                messagebox.showinfo("Already Added", f"{ticker} is already in your watchlist")
        
        entry.bind('<Return>', lambda e: add_it())
        
        tk.Button(dialog, text="Add", command=add_it,
                 font=('Arial', 10, 'bold'), bg=self.colors['accent'],
                 fg='white', bd=0, padx=20, pady=8,
                 cursor='hand2').pack(pady=10)
    
    def add_to_watchlist(self):
        """Add current stock to watchlist"""
        if self.current_ticker and self.current_ticker not in self.watchlist:
            self.watchlist.append(self.current_ticker)
            self.save_watchlist()
            messagebox.showinfo("Added", f"{self.current_ticker} added to watchlist!")
            self.add_watchlist_btn.config(text="✓ In Watchlist", state='disabled')
    
    def remove_from_watchlist_ui(self, ticker, card_widget):
        """Remove from watchlist with UI update"""
        if ticker in self.watchlist:
            self.watchlist.remove(ticker)
            self.save_watchlist()
            card_widget.destroy()
    
    def set_alert(self):
        """Set price alert"""
        if not self.current_ticker:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Set Alert")
        dialog.geometry("350x250")
        dialog.configure(bg=self.colors['bg'])
        dialog.resizable(False, False)
        
        tk.Label(dialog, text=f"Set Alert for {self.current_ticker}",
                font=('Arial', 12, 'bold'), fg=self.colors['text'],
                bg=self.colors['bg']).pack(pady=20)
        
        tk.Label(dialog, text="Alert when price goes:",
                font=('Arial', 10), fg=self.colors['text'],
                bg=self.colors['bg']).pack()
        
        alert_type = tk.StringVar(value="above")
        
        tk.Radiobutton(dialog, text="Above", variable=alert_type, value="above",
                      font=('Arial', 10), bg=self.colors['bg'], fg=self.colors['text'],
                      selectcolor=self.colors['card'], activebackground=self.colors['bg'],
                      activeforeground=self.colors['text']).pack()
        
        tk.Radiobutton(dialog, text="Below", variable=alert_type, value="below",
                      font=('Arial', 10), bg=self.colors['bg'], fg=self.colors['text'],
                      selectcolor=self.colors['card'], activebackground=self.colors['bg'],
                      activeforeground=self.colors['text']).pack()
        
        tk.Label(dialog, text="Target price:",
                font=('Arial', 10), fg=self.colors['text'],
                bg=self.colors['bg']).pack(pady=(10,5))
        
        price_entry = tk.Entry(dialog, font=('Arial', 11), width=15,
                              bg=self.colors['card'], fg=self.colors['text'],
                              insertbackground=self.colors['accent'], bd=1, relief='solid')
        price_entry.pack()
        
        def save_alert():
            try:
                price = float(price_entry.get())
                self.alerts[self.current_ticker] = {
                    'type': alert_type.get(),
                    'price': price
                }
                self.save_alerts()
                messagebox.showinfo("Alert Set", 
                                  f"You'll be notified when {self.current_ticker} goes {alert_type.get()} ${price:.2f}\n\n(Note: Real-time monitoring coming soon)")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Invalid Price", "Please enter a valid number")
        
        tk.Button(dialog, text="Set Alert", command=save_alert,
                 font=('Arial', 10, 'bold'), bg=self.colors['accent'],
                 fg='white', bd=0, padx=20, pady=8,
                 cursor='hand2').pack(pady=20)
    
    def export_menu(self):
        """Show export options"""
        if not self.current_ticker:
            messagebox.showwarning("No Data", "Analyze a stock first!")
            return
        
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="📊 Export Chart (PNG)", command=self.export_chart_png)
        menu.add_command(label="📄 Export Analysis (TXT)", command=self.export_analysis_txt)
        menu.add_command(label="📑 Export Data (CSV)", command=self.export_data_csv)
        
        # Show menu at mouse position
        menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
    
    def export_chart_png(self):
        """Export chart as PNG"""
        if not hasattr(self, 'current_canvas') or not self.current_ticker:
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=f"{self.current_ticker}_chart_{datetime.now().strftime('%Y%m%d')}.png",
            filetypes=[("PNG", "*.png"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                self.current_canvas.figure.savefig(filename, dpi=300,
                                                   bbox_inches='tight',
                                                   facecolor=self.colors['card'])
                messagebox.showinfo("Success", "Chart exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")
    
    def export_analysis_txt(self):
        """Export analysis as text"""
        if not self.current_ticker:
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"{self.current_ticker}_analysis_{datetime.now().strftime('%Y%m%d')}.txt",
            filetypes=[("Text", "*.txt"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(f"Stock Analysis Report - {self.current_ticker}\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("="*60 + "\n\n")
                    f.write("STOCK INFORMATION\n")
                    f.write("-"*60 + "\n")
                    f.write(self.info_text.get(1.0, tk.END))
                    f.write("\n\nTRADING SIGNALS\n")
                    f.write("-"*60 + "\n")
                    f.write(self.signals_text.get(1.0, tk.END))
                messagebox.showinfo("Success", "Analysis exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")
    
    def export_data_csv(self):
        """Export data as CSV"""
        if self.chart_data is None:
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=f"{self.current_ticker}_data_{datetime.now().strftime('%Y%m%d')}.csv",
            filetypes=[("CSV", "*.csv"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                self.chart_data.to_csv(filename)
                messagebox.showinfo("Success", "Data exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = StockAnalyzerPremium(root)
    root.mainloop()
