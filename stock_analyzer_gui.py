"""
Stock Analyzer Pro - ULTRA Premium Edition
Advanced professional stock analysis platform
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
from matplotlib.widgets import Cursor
import threading
from datetime import datetime, timedelta
import json
import os

class StockAnalyzerUltra:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Analyzer Pro - Ultra Premium")
        
        # Window setup
        window_width = 1900
        window_height = 1050
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Theme
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
        self.comparison_data = {}
        
        # Indicator settings - with adjustable parameters
        self.show_ma20 = tk.BooleanVar(value=True)
        self.show_ma50 = tk.BooleanVar(value=True)
        self.show_ma200 = tk.BooleanVar(value=False)
        self.show_bollinger = tk.BooleanVar(value=True)
        self.show_rsi = tk.BooleanVar(value=True)
        self.show_macd = tk.BooleanVar(value=True)
        self.show_volume = tk.BooleanVar(value=True)
        
        # Adjustable parameters
        self.ma20_period = tk.IntVar(value=20)
        self.ma50_period = tk.IntVar(value=50)
        self.ma200_period = tk.IntVar(value=200)
        self.rsi_period = tk.IntVar(value=14)
        self.bb_period = tk.IntVar(value=20)
        self.bb_std = tk.DoubleVar(value=2.0)
        
        self.chart_type = tk.StringVar(value="candlestick")
        self.compare_mode = False
        self.compare_tickers = []
        
        # Build UI
        self.build_ui()
        
    def load_watchlist(self):
        if os.path.exists(self.watchlist_file):
            try:
                with open(self.watchlist_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
                    return {'stocks': data if isinstance(data, list) else [], 'starred': [], 'alerts': []}
            except:
                return {'stocks': [], 'starred': [], 'alerts': []}
        return {'stocks': [], 'starred': [], 'alerts': []}
    
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
        for widget in self.root.winfo_children():
            widget.destroy()
        self.build_ui()
        if self.current_ticker and self.chart_data is not None:
            self.create_chart(self.chart_data, self.current_ticker, None)
    
    def build_ui(self):
        """Build ultra premium UI"""
        self.root.configure(bg=self.colors['bg'])
        
        # Top bar
        top_bar = tk.Frame(self.root, bg=self.colors['card'], height=85)
        top_bar.pack(side=tk.TOP, fill=tk.X)
        top_bar.pack_propagate(False)
        
        # Logo
        logo_frame = tk.Frame(top_bar, bg=self.colors['card'])
        logo_frame.pack(side=tk.LEFT, padx=25, pady=15)
        
        tk.Label(logo_frame, text="📊 Stock Analyzer", 
                font=('Arial', 17, 'bold'),
                fg=self.colors['accent'], bg=self.colors['card']).pack()
        tk.Label(logo_frame, text="Ultra Premium Edition", 
                font=('Arial', 8),
                fg=self.colors['text_dim'], bg=self.colors['card']).pack()
        
        # Search area
        search_card = tk.Frame(top_bar, bg=self.colors['sidebar'], relief='flat')
        search_card.pack(side=tk.LEFT, padx=20, pady=12)
        
        search_inner = tk.Frame(search_card, bg=self.colors['sidebar'])
        search_inner.pack(padx=18, pady=12)
        
        # Ticker
        tk.Label(search_inner, text="Ticker:", font=('Arial', 9, 'bold'),
                fg=self.colors['text'], bg=self.colors['sidebar']).grid(row=0, column=0, padx=(0,5))
        
        self.ticker_entry = tk.Entry(search_inner, font=('Arial', 11), width=10,
                                     bg=self.colors['card'], fg=self.colors['text'],
                                     insertbackground=self.colors['accent'], bd=1, relief='solid')
        self.ticker_entry.grid(row=0, column=1, padx=5)
        self.ticker_entry.bind('<Return>', lambda e: self.analyze())
        
        # Chart type
        tk.Label(search_inner, text="Type:", font=('Arial', 9, 'bold'),
                fg=self.colors['text'], bg=self.colors['sidebar']).grid(row=0, column=2, padx=(15,5))
        
        chart_combo = ttk.Combobox(search_inner, textvariable=self.chart_type,
                                   values=["candlestick", "line"],
                                   width=10, state='readonly', font=('Arial', 9))
        chart_combo.grid(row=0, column=3, padx=5)
        
        # Analyze button
        analyze_btn = tk.Button(search_inner, text="⚡ ANALYZE", command=self.analyze,
                               font=('Arial', 11, 'bold'), bg=self.colors['accent'],
                               fg='white', bd=0, padx=25, pady=10, cursor='hand2')
        analyze_btn.grid(row=0, column=4, padx=15)
        
        # Quick timeframe buttons
        quick_frame = tk.Frame(top_bar, bg=self.colors['card'])
        quick_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(quick_frame, text="Period:", font=('Arial', 8, 'bold'),
                fg=self.colors['text_dim'], bg=self.colors['card']).pack()
        
        periods_frame = tk.Frame(quick_frame, bg=self.colors['card'])
        periods_frame.pack()
        
        self.period_var = tk.StringVar(value="1y")
        for period in ["1W", "1M", "3M", "6M", "1Y", "2Y", "5Y"]:
            period_val = period.lower().replace('w', 'd').replace('d', 'd')
            if period == "1W":
                period_val = "5d"
            elif period == "1M":
                period_val = "1mo"
            elif period == "3M":
                period_val = "3mo"
            elif period == "6M":
                period_val = "6mo"
            elif period == "1Y":
                period_val = "1y"
            elif period == "2Y":
                period_val = "2y"
            elif period == "5Y":
                period_val = "5y"
            
            btn = tk.Button(periods_frame, text=period,
                          command=lambda p=period_val: self.set_period(p),
                          font=('Arial', 8, 'bold'),
                          bg=self.colors['sidebar'] if self.period_var.get() != period_val else self.colors['accent'],
                          fg=self.colors['text'] if self.period_var.get() != period_val else 'white',
                          bd=0, padx=8, pady=4, cursor='hand2')
            btn.pack(side=tk.LEFT, padx=2)
        
        # Right buttons
        btn_frame = tk.Frame(top_bar, bg=self.colors['card'])
        btn_frame.pack(side=tk.RIGHT, padx=25, pady=15)
        
        # Theme toggle
        theme_icon = "🌙" if self.current_theme == "dark" else "☀️"
        tk.Button(btn_frame, text=theme_icon, command=self.toggle_theme,
                 font=('Arial', 15), bg=self.colors['sidebar'],
                 fg=self.colors['text'], bd=0, padx=12, pady=6,
                 cursor='hand2').pack(side=tk.LEFT, padx=4)
        
        # Indicators with icon
        tk.Button(btn_frame, text="⚙️", command=self.show_advanced_indicators,
                 font=('Arial', 15), bg=self.colors['sidebar'],
                 fg=self.colors['text'], bd=0, padx=12, pady=6,
                 cursor='hand2').pack(side=tk.LEFT, padx=4)
        
        # Compare
        tk.Button(btn_frame, text="📈 Compare", command=self.toggle_compare_mode,
                 font=('Arial', 9, 'bold'), bg=self.colors['warning'] if self.compare_mode else self.colors['sidebar'],
                 fg='white' if self.compare_mode else self.colors['text'],
                 bd=0, padx=12, pady=8, cursor='hand2').pack(side=tk.LEFT, padx=4)
        
        # Watchlist
        tk.Button(btn_frame, text="⭐", command=self.show_watchlist,
                 font=('Arial', 15), bg=self.colors['sidebar'],
                 fg=self.colors['warning'], bd=0, padx=12, pady=6,
                 cursor='hand2').pack(side=tk.LEFT, padx=4)
        
        # Export
        tk.Button(btn_frame, text="💾", command=self.export_menu,
                 font=('Arial', 15), bg=self.colors['sidebar'],
                 fg=self.colors['success'], bd=0, padx=12, pady=6,
                 cursor='hand2').pack(side=tk.LEFT, padx=4)
        
        # Main content
        main = tk.Frame(self.root, bg=self.colors['bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Left panel
        left = tk.Frame(main, bg=self.colors['bg'], width=400)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0,15))
        left.pack_propagate(False)
        
        # Stock Info Card
        info_card = self.create_card(left, "📈 Stock Information")
        self.info_text = tk.Text(info_card, bg=self.colors['card'], 
                                fg=self.colors['text'],
                                font=('Courier', 9), bd=0, wrap=tk.WORD, 
                                height=10, relief='flat')
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0,15))
        
        # AI Insight Card
        insight_card = self.create_card(left, "🤖 AI Market Insight")
        self.insight_text = scrolledtext.ScrolledText(insight_card, bg=self.colors['card'],
                                   fg=self.colors['text'],
                                   font=('Arial', 9), bd=0, wrap=tk.WORD,
                                   height=8, relief='flat')
        self.insight_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0,15))
        
        # Trading Signals Card
        signals_card = self.create_card(left, "🎯 Trading Signals")
        self.signals_text = scrolledtext.ScrolledText(signals_card, bg=self.colors['card'],
                                   fg=self.colors['text'],
                                   font=('Courier', 9), bd=0, wrap=tk.WORD,
                                   height=12, relief='flat')
        self.signals_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0,15))
        
        # Recommendation Card
        rec_card = self.create_card(left, "💡 Recommendation")
        self.rec_frame = tk.Frame(rec_card, bg=self.colors['card'])
        self.rec_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0,15))
        
        tk.Label(self.rec_frame, text="Analyze a stock to see recommendations",
                font=('Arial', 10), fg=self.colors['text_dim'],
                bg=self.colors['card'], wraplength=360).pack(pady=30)
        
        # Right panel - Chart
        right = tk.Frame(main, bg=self.colors['bg'])
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Chart card
        chart_card = tk.Frame(right, bg=self.colors['card'], relief='flat')
        chart_card.pack(fill=tk.BOTH, expand=True)
        
        # Chart header
        chart_header = tk.Frame(chart_card, bg=self.colors['card'], height=60)
        chart_header.pack(fill=tk.X)
        chart_header.pack_propagate(False)
        
        header_left = tk.Frame(chart_header, bg=self.colors['card'])
        header_left.pack(side=tk.LEFT, pady=15, padx=25)
        
        self.chart_title = tk.Label(header_left, text="Select a stock to begin", 
                                    font=('Arial', 14, 'bold'),
                                    fg=self.colors['text'], bg=self.colors['card'])
        self.chart_title.pack(side=tk.LEFT)
        
        self.price_label = tk.Label(header_left, text="", 
                                    font=('Arial', 12),
                                    fg=self.colors['text_dim'], bg=self.colors['card'])
        self.price_label.pack(side=tk.LEFT, padx=15)
        
        # Header buttons
        header_right = tk.Frame(chart_header, bg=self.colors['card'])
        header_right.pack(side=tk.RIGHT, pady=15, padx=25)
        
        self.add_watchlist_btn = tk.Button(header_right, text="⭐ Add",
                                          command=self.add_to_watchlist,
                                          font=('Arial', 9, 'bold'), bg=self.colors['warning'],
                                          fg='white', bd=0, padx=12, pady=7,
                                          cursor='hand2', state='disabled')
        self.add_watchlist_btn.pack(side=tk.LEFT, padx=4)
        
        self.alert_btn = tk.Button(header_right, text="🔔 Alert",
                                   command=self.set_alert,
                                   font=('Arial', 9, 'bold'), bg=self.colors['accent'],
                                   fg='white', bd=0, padx=12, pady=7,
                                   cursor='hand2', state='disabled')
        self.alert_btn.pack(side=tk.LEFT, padx=4)
        
        # Separator
        tk.Frame(chart_card, bg=self.colors['border'], height=1).pack(fill=tk.X)
        
        # Chart area
        self.chart_frame = tk.Frame(chart_card, bg=self.colors['card'])
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Welcome
        self.show_welcome()
        
        # Status bar
        status = tk.Frame(self.root, bg=self.colors['card'], height=38)
        status.pack(side=tk.BOTTOM, fill=tk.X)
        status.pack_propagate(False)
        
        tk.Frame(status, bg=self.colors['border'], height=1).pack(side=tk.TOP, fill=tk.X)
        
        self.status_label = tk.Label(status, text="Ready • Ultra Premium Edition", 
                                     font=('Arial', 9),
                                     fg=self.colors['text_dim'], bg=self.colors['card'])
        self.status_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.progress = ttk.Progressbar(status, mode='indeterminate', length=150)
    
    def set_period(self, period):
        """Set period and re-analyze"""
        self.period_var.set(period)
        if self.current_ticker:
            self.analyze()
    
    def create_card(self, parent, title):
        """Create modern card"""
        card_outer = tk.Frame(parent, bg=self.colors['bg'])
        card_outer.pack(fill=tk.X, pady=(0, 15))
        
        card = tk.Frame(card_outer, bg=self.colors['card'], 
                       relief='flat', highlightbackground=self.colors['border'],
                       highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)
        
        header = tk.Frame(card, bg=self.colors['card'], height=48)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text=title, font=('Arial', 11, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT, 
                                                                      padx=15, pady=14)
        
        tk.Frame(card, bg=self.colors['border'], height=1).pack(fill=tk.X)
        
        return card
    
    def show_welcome(self):
        """Welcome screen"""
        welcome = tk.Frame(self.chart_frame, bg=self.colors['card'])
        welcome.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(welcome, text="📊", font=('Arial', 75),
                fg=self.colors['accent'], bg=self.colors['card']).pack()
        
        tk.Label(welcome, text="Ultra Professional Analysis",
                font=('Arial', 24, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack(pady=18)
        
        tk.Label(welcome, text="Advanced indicators • AI insights • Real-time tooltips\nCompare stocks • Custom parameters • Export suite",
                font=('Arial', 11),
                fg=self.colors['text_dim'], bg=self.colors['card'],
                justify=tk.CENTER).pack(pady=12)
        
        # Popular stocks
        quick_frame = tk.Frame(welcome, bg=self.colors['card'])
        quick_frame.pack(pady=28)
        
        tk.Label(quick_frame, text="Quick Start: ", font=('Arial', 10, 'bold'),
                fg=self.colors['text_dim'], bg=self.colors['card']).pack(side=tk.LEFT, padx=5)
        
        for ticker in ["AAPL", "TSLA", "GOOGL", "MSFT", "NVDA", "AMZN"]:
            btn = tk.Button(quick_frame, text=ticker,
                          command=lambda t=ticker: self.quick_analyze(t),
                          font=('Arial', 10, 'bold'), 
                          bg=self.colors['sidebar'],
                          fg=self.colors['accent'], bd=0, padx=16, pady=8,
                          cursor='hand2')
            btn.pack(side=tk.LEFT, padx=4)
    
    def quick_analyze(self, ticker):
        self.ticker_entry.delete(0, tk.END)
        self.ticker_entry.insert(0, ticker)
        self.analyze()
    
    def show_advanced_indicators(self):
        """Advanced indicators panel with sliders"""
        win = tk.Toplevel(self.root)
        win.title("⚙️ Advanced Indicators")
        win.geometry("450x550")
        win.configure(bg=self.colors['bg'])
        win.resizable(False, False)
        
        # Header
        header = tk.Frame(win, bg=self.colors['card'], height=65)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="⚙️ Customize Indicators", font=('Arial', 14, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack(pady=22, padx=25, anchor=tk.W)
        
        tk.Frame(header, bg=self.colors['border'], height=1).pack(side=tk.BOTTOM, fill=tk.X)
        
        # Content
        content = tk.Frame(win, bg=self.colors['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Scrollable frame
        canvas = tk.Canvas(content, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(content, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Moving Averages
        tk.Label(scrollable, text="MOVING AVERAGES", font=('Arial', 10, 'bold'),
                fg=self.colors['text'], bg=self.colors['bg']).pack(anchor=tk.W, pady=(0,10))
        
        self.create_indicator_control(scrollable, "MA-20", self.show_ma20, self.ma20_period, 5, 200)
        self.create_indicator_control(scrollable, "MA-50", self.show_ma50, self.ma50_period, 10, 200)
        self.create_indicator_control(scrollable, "MA-200", self.show_ma200, self.ma200_period, 50, 300)
        
        # Other Indicators
        tk.Label(scrollable, text="OTHER INDICATORS", font=('Arial', 10, 'bold'),
                fg=self.colors['text'], bg=self.colors['bg']).pack(anchor=tk.W, pady=(20,10))
        
        tk.Checkbutton(scrollable, text="RSI", variable=self.show_rsi,
                      font=('Arial', 10), bg=self.colors['bg'], fg=self.colors['text'],
                      selectcolor=self.colors['card']).pack(anchor=tk.W, pady=5)
        
        tk.Checkbutton(scrollable, text="MACD", variable=self.show_macd,
                      font=('Arial', 10), bg=self.colors['bg'], fg=self.colors['text'],
                      selectcolor=self.colors['card']).pack(anchor=tk.W, pady=5)
        
        tk.Checkbutton(scrollable, text="Bollinger Bands", variable=self.show_bollinger,
                      font=('Arial', 10), bg=self.colors['bg'], fg=self.colors['text'],
                      selectcolor=self.colors['card']).pack(anchor=tk.W, pady=5)
        
        tk.Checkbutton(scrollable, text="Volume", variable=self.show_volume,
                      font=('Arial', 10), bg=self.colors['bg'], fg=self.colors['text'],
                      selectcolor=self.colors['card']).pack(anchor=tk.W, pady=5)
        
        # Apply button
        tk.Button(scrollable, text="✓ Apply & Refresh Chart", 
                 command=lambda: [self.refresh_chart(), win.destroy()],
                 font=('Arial', 11, 'bold'), bg=self.colors['accent'],
                 fg='white', bd=0, padx=25, pady=12,
                 cursor='hand2').pack(pady=25)
    
    def create_indicator_control(self, parent, name, show_var, period_var, min_val, max_val):
        """Create indicator with toggle and slider"""
        frame = tk.Frame(parent, bg=self.colors['card'])
        frame.pack(fill=tk.X, pady=8, padx=5)
        
        inner = tk.Frame(frame, bg=self.colors['card'])
        inner.pack(padx=15, pady=12)
        
        # Checkbox
        tk.Checkbutton(inner, text=name, variable=show_var,
                      font=('Arial', 10, 'bold'), bg=self.colors['card'],
                      fg=self.colors['text'], selectcolor=self.colors['sidebar'],
                      width=10, anchor=tk.W).grid(row=0, column=0, sticky=tk.W)
        
        # Slider
        slider = tk.Scale(inner, from_=min_val, to=max_val,
                         orient=tk.HORIZONTAL, variable=period_var,
                         bg=self.colors['card'], fg=self.colors['text'],
                         highlightthickness=0, troughcolor=self.colors['sidebar'],
                         activebackground=self.colors['accent'],
                         length=200)
        slider.grid(row=0, column=1, padx=10)
        
        # Value label
        value_label = tk.Label(inner, textvariable=period_var,
                              font=('Arial', 10, 'bold'), fg=self.colors['accent'],
                              bg=self.colors['card'], width=4)
        value_label.grid(row=0, column=2)
    
    def toggle_compare_mode(self):
        """Toggle compare mode"""
        self.compare_mode = not self.compare_mode
        if self.compare_mode:
            self.show_compare_dialog()
        else:
            self.compare_tickers = []
            if self.current_ticker:
                self.analyze()
    
    def show_compare_dialog(self):
        """Show dialog to add tickers for comparison"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Compare Stocks")
        dialog.geometry("400x300")
        dialog.configure(bg=self.colors['bg'])
        dialog.resizable(False, False)
        
        tk.Label(dialog, text="📈 Compare Multiple Stocks",
                font=('Arial', 13, 'bold'), fg=self.colors['text'],
                bg=self.colors['bg']).pack(pady=20)
        
        tk.Label(dialog, text="Enter tickers separated by commas:",
                font=('Arial', 10), fg=self.colors['text'],
                bg=self.colors['bg']).pack(pady=10)
        
        entry = tk.Entry(dialog, font=('Arial', 11), width=30,
                        bg=self.colors['card'], fg=self.colors['text'],
                        insertbackground=self.colors['accent'], bd=1, relief='solid')
        entry.pack(pady=10, padx=20)
        entry.insert(0, "AAPL, MSFT, GOOGL")
        
        def compare():
            tickers = [t.strip().upper() for t in entry.get().split(',')]
            self.compare_tickers = tickers
            dialog.destroy()
            if tickers:
                self.compare_stocks(tickers)
        
        tk.Button(dialog, text="Compare", command=compare,
                 font=('Arial', 10, 'bold'), bg=self.colors['accent'],
                 fg='white', bd=0, padx=20, pady=10,
                 cursor='hand2').pack(pady=20)
    
    def compare_stocks(self, tickers):
        """Compare multiple stocks"""
        self.status_label.config(text=f"Comparing {len(tickers)} stocks...")
        self.progress.pack(side=tk.RIGHT, padx=20)
        self.progress.start(10)
        
        thread = threading.Thread(target=self._compare_thread, args=(tickers,))
        thread.daemon = True
        thread.start()
    
    def _compare_thread(self, tickers):
        """Comparison thread"""
        try:
            period = self.period_var.get()
            comparison_data = {}
            
            for ticker in tickers:
                stock = yf.Ticker(ticker)
                data = stock.history(period=period)
                if not data.empty:
                    comparison_data[ticker] = data
            
            if comparison_data:
                self.comparison_data = comparison_data
                self.root.after(0, self.create_comparison_chart, comparison_data)
                self.root.after(0, self.status_label.config,
                              {'text': f'Comparing {len(tickers)} stocks'})
            
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", f"Comparison failed:\n{str(e)}")
        finally:
            self.root.after(0, self.progress.stop)
            self.root.after(0, self.progress.pack_forget)
    
    def create_comparison_chart(self, comparison_data):
        """Create comparison chart"""
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        self.chart_title.config(text=f"Comparing {len(comparison_data)} Stocks")
        self.price_label.config(text="")
        
        # Normalize prices to percentage change
        fig = plt.figure(figsize=(16, 10), facecolor=self.colors['card'])
        ax = fig.add_subplot(111)
        
        ax.set_facecolor(self.colors['card'])
        for spine in ax.spines.values():
            spine.set_color(self.colors['border'])
        ax.tick_params(colors=self.colors['text_dim'], labelsize=10)
        ax.grid(True, alpha=0.2, color=self.colors['border'])
        
        colors_list = [self.colors['accent'], self.colors['success'], 
                      self.colors['danger'], self.colors['warning'],
                      '#ff79c6', '#bd93f9']
        
        for idx, (ticker, data) in enumerate(comparison_data.items()):
            # Normalize to percentage change from first day
            normalized = (data['Close'] / data['Close'].iloc[0] - 1) * 100
            color = colors_list[idx % len(colors_list)]
            ax.plot(data.index, normalized, linewidth=2.5, label=ticker, color=color)
        
        ax.set_ylabel('% Change', color=self.colors['text'], fontsize=12, fontweight='bold')
        ax.set_xlabel('Date', color=self.colors['text'], fontsize=12)
        ax.set_title('Stock Performance Comparison (Normalized)', 
                    color=self.colors['text'], fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper left', fontsize=11, framealpha=0.9,
                 facecolor=self.colors['card'], edgecolor=self.colors['border'])
        ax.axhline(0, color=self.colors['text_dim'], linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        
        toolbar = NavigationToolbar2Tk(canvas, self.chart_frame)
        toolbar.update()
        toolbar.config(bg=self.colors['sidebar'])
        
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.current_canvas = canvas
    
    def refresh_chart(self):
        if self.current_ticker and self.chart_data is not None:
            self.create_chart(self.chart_data, self.current_ticker, None)
    
    def analyze(self):
        ticker = self.ticker_entry.get().strip().upper()
        if not ticker:
            messagebox.showwarning("Input Required", "Please enter a ticker")
            return
        
        self.current_ticker = ticker
        self.status_label.config(text=f"Analyzing {ticker}...")
        self.progress.pack(side=tk.RIGHT, padx=20)
        self.progress.start(10)
        
        self.info_text.delete(1.0, tk.END)
        self.insight_text.delete(1.0, tk.END)
        self.signals_text.delete(1.0, tk.END)
        
        thread = threading.Thread(target=self._analyze_thread, args=(ticker,))
        thread.daemon = True
        thread.start()
    
    def _analyze_thread(self, ticker):
        try:
            period = self.period_var.get()
            
            stock = yf.Ticker(ticker)
            data = stock.history(period=period)
            
            if data.empty:
                self.root.after(0, messagebox.showerror, "Error", f"No data for {ticker}")
                return
            
            data = self.calculate_indicators(data)
            self.chart_data = data
            
            self.root.after(0, self.create_chart, data, ticker, stock)
            self.root.after(0, self.show_analysis, data, ticker, stock)
            
            # Enable buttons
            if ticker not in self.watchlist.get('stocks', []):
                self.root.after(0, self.add_watchlist_btn.config,
                              {'text': '⭐ Add', 'state': 'normal'})
            else:
                self.root.after(0, self.add_watchlist_btn.config,
                              {'text': '✓ Added', 'state': 'disabled'})
            
            self.root.after(0, self.alert_btn.config, {'state': 'normal'})
            self.root.after(0, self.status_label.config, {'text': f'Analysis complete • {ticker}'})
            
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", f"Failed:\n{str(e)}")
            self.root.after(0, self.status_label.config, {'text': 'Error'})
        finally:
            self.root.after(0, self.progress.stop)
            self.root.after(0, self.progress.pack_forget)
    
    def calculate_indicators(self, data):
        # Moving averages with custom periods
        data[f'MA_{self.ma20_period.get()}'] = data['Close'].rolling(window=self.ma20_period.get()).mean()
        data[f'MA_{self.ma50_period.get()}'] = data['Close'].rolling(window=self.ma50_period.get()).mean()
        data[f'MA_{self.ma200_period.get()}'] = data['Close'].rolling(window=self.ma200_period.get()).mean()
        
        # For compatibility
        data['MA_20'] = data[f'MA_{self.ma20_period.get()}']
        data['MA_50'] = data[f'MA_{self.ma50_period.get()}']
        data['MA_200'] = data[f'MA_{self.ma200_period.get()}']
        
        # RSI
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=self.rsi_period.get()).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=self.rsi_period.get()).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = data['Close'].ewm(span=12, adjust=False).mean()
        ema_26 = data['Close'].ewm(span=26, adjust=False).mean()
        data['MACD'] = ema_12 - ema_26
        data['MACD_Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
        data['MACD_Hist'] = data['MACD'] - data['MACD_Signal']
        
        # Bollinger Bands
        sma = data['Close'].rolling(window=self.bb_period.get()).mean()
        std = data['Close'].rolling(window=self.bb_period.get()).std()
        data['BB_Upper'] = sma + (std * self.bb_std.get())
        data['BB_Lower'] = sma - (std * self.bb_std.get())
        
        # Volume MA
        data['Volume_MA'] = data['Volume'].rolling(window=20).mean()
        
        return data
    
    def create_chart(self, data, ticker, stock):
        """Create enhanced chart with better tooltips"""
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        current_price = data['Close'].iloc[-1]
        prev_price = data['Close'].iloc[-2]
        change = ((current_price - prev_price) / prev_price) * 100
        change_color = self.colors['success'] if change >= 0 else self.colors['danger']
        
        self.chart_title.config(text=f"{ticker} • {self.period_var.get().upper()}")
        self.price_label.config(text=f"${current_price:.2f} ({change:+.2f}%)", fg=change_color)
        
        # Determine subplot layout
        n_subplots = 1  # Always price
        if self.show_volume.get():
            n_subplots += 1
        if self.show_rsi.get():
            n_subplots += 1
        if self.show_macd.get():
            n_subplots += 1
        
        ratios = [3] + [1] * (n_subplots - 1)
        
        fig = plt.figure(figsize=(16, 11), facecolor=self.colors['card'])
        gs = fig.add_gridspec(n_subplots, 1, height_ratios=ratios, hspace=0.06)
        
        axes = []
        ax1 = fig.add_subplot(gs[0])
        axes.append(ax1)
        
        subplot_idx = 1
        if self.show_volume.get():
            ax2 = fig.add_subplot(gs[subplot_idx], sharex=ax1)
            axes.append(ax2)
            subplot_idx += 1
        
        if self.show_rsi.get():
            ax3 = fig.add_subplot(gs[subplot_idx], sharex=ax1)
            axes.append(ax3)
            subplot_idx += 1
        
        if self.show_macd.get():
            ax4 = fig.add_subplot(gs[subplot_idx], sharex=ax1)
            axes.append(ax4)
        
        # Style axes
        for ax in axes:
            ax.set_facecolor(self.colors['card'])
            for spine in ax.spines.values():
                spine.set_color(self.colors['border'])
            ax.tick_params(colors=self.colors['text_dim'], labelsize=10)
            ax.grid(True, alpha=0.15, color=self.colors['border'], linestyle='-')
        
        # PRICE CHART with better visuals
        if self.chart_type.get() == "candlestick":
            self.plot_candlesticks(ax1, data)
        else:
            ax1.plot(data.index, data['Close'], linewidth=3,
                    color=self.colors['accent'], label='Close', zorder=5)
        
        # Moving averages
        if self.show_ma20.get():
            ax1.plot(data.index, data['MA_20'], linewidth=2.5,
                    label=f'MA {self.ma20_period.get()}', 
                    color=self.colors['success'], alpha=0.9, zorder=4)
        
        if self.show_ma50.get():
            ax1.plot(data.index, data['MA_50'], linewidth=2.5,
                    label=f'MA {self.ma50_period.get()}',
                    color=self.colors['warning'], alpha=0.9, zorder=4)
        
        if self.show_ma200.get() and pd.notna(data['MA_200'].iloc[-1]):
            ax1.plot(data.index, data['MA_200'], linewidth=2,
                    label=f'MA {self.ma200_period.get()}',
                    color=self.colors['danger'], alpha=0.7, zorder=3)
        
        # ENHANCED Bollinger Bands - more visible!
        if self.show_bollinger.get():
            ax1.fill_between(data.index, data['BB_Upper'], data['BB_Lower'],
                            alpha=0.20, color=self.colors['accent'], zorder=1, 
                            label='Bollinger Bands')
            ax1.plot(data.index, data['BB_Upper'], linewidth=2,
                    color=self.colors['accent'], alpha=0.6, linestyle='--', zorder=2)
            ax1.plot(data.index, data['BB_Lower'], linewidth=2,
                    color=self.colors['accent'], alpha=0.6, linestyle='--', zorder=2)
        
        ax1.set_ylabel('Price ($)', color=self.colors['text'], fontsize=12, fontweight='bold')
        ax1.set_title(f'{ticker} Technical Analysis', color=self.colors['text'],
                     fontsize=14, fontweight='bold', pad=18)
        ax1.legend(loc='upper left', fontsize=10, framealpha=0.95,
                  facecolor=self.colors['card'], edgecolor=self.colors['border'])
        
        # VOLUME (if enabled)
        if self.show_volume.get():
            ax_vol = axes[1]
            colors = [self.colors['success'] if data['Close'].iloc[i] >= data['Open'].iloc[i]
                     else self.colors['danger'] for i in range(len(data))]
            ax_vol.bar(data.index, data['Volume'], color=colors, alpha=0.7, width=0.8)
            ax_vol.plot(data.index, data['Volume_MA'], linewidth=2.5,
                       color=self.colors['warning'], label='Volume MA', alpha=0.9)
            ax_vol.set_ylabel('Volume', color=self.colors['text'], fontsize=11, fontweight='bold')
            ax_vol.legend(loc='upper left', fontsize=9, framealpha=0.9)
            ax_vol.yaxis.set_major_formatter(plt.FuncFormatter(
                lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else f'{x/1e3:.0f}K'))
        
        # RSI (if enabled) with VISIBLE thresholds
        if self.show_rsi.get():
            ax_rsi = axes[2] if self.show_volume.get() else axes[1]
            ax_rsi.plot(data.index, data['RSI'], linewidth=3,
                       color=self.colors['accent'], label='RSI')
            
            # PROMINENT threshold lines
            ax_rsi.axhline(y=70, color=self.colors['danger'], linestyle='-', 
                          alpha=0.8, linewidth=2.5, label='Overbought (70)')
            ax_rsi.axhline(y=30, color=self.colors['success'], linestyle='-',
                          alpha=0.8, linewidth=2.5, label='Oversold (30)')
            
            # Enhanced shaded zones
            ax_rsi.fill_between(data.index, 70, 100, alpha=0.2, color=self.colors['danger'])
            ax_rsi.fill_between(data.index, 0, 30, alpha=0.2, color=self.colors['success'])
            
            ax_rsi.set_ylabel('RSI', color=self.colors['text'], fontsize=11, fontweight='bold')
            ax_rsi.set_ylim(0, 100)
            ax_rsi.legend(loc='upper left', fontsize=9, framealpha=0.9)
        
        # MACD (if enabled) with ZERO line
        if self.show_macd.get():
            ax_macd = axes[-1]
            ax_macd.plot(data.index, data['MACD'], linewidth=2.5,
                        color=self.colors['accent'], label='MACD')
            ax_macd.plot(data.index, data['MACD_Signal'], linewidth=2.5,
                        color=self.colors['warning'], label='Signal')
            
            macd_colors = [self.colors['success'] if val >= 0 else self.colors['danger']
                          for val in data['MACD_Hist']]
            ax_macd.bar(data.index, data['MACD_Hist'], color=macd_colors, alpha=0.6, width=0.8)
            
            # PROMINENT zero line
            ax_macd.axhline(0, color=self.colors['text'], linewidth=2, 
                           linestyle='-', alpha=0.6, label='Zero Line')
            
            ax_macd.set_ylabel('MACD', color=self.colors['text'], fontsize=11, fontweight='bold')
            ax_macd.set_xlabel('Date', color=self.colors['text'], fontsize=11)
            ax_macd.legend(loc='upper left', fontsize=9, framealpha=0.9)
        else:
            axes[-1].set_xlabel('Date', color=self.colors['text'], fontsize=11)
        
        # Hide x labels except bottom
        for ax in axes[:-1]:
            plt.setp(ax.get_xticklabels(), visible=False)
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        
        # Toolbar
        toolbar = NavigationToolbar2Tk(canvas, self.chart_frame)
        toolbar.update()
        toolbar.config(bg=self.colors['sidebar'])
        
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.current_canvas = canvas
        
        # Enhanced tooltip on hover
        self.setup_tooltip(canvas, data, ax1)
    
    def setup_tooltip(self, canvas, data, ax):
        """Enhanced tooltip with all data"""
        self.tooltip_text = None
        
        def on_hover(event):
            if event.inaxes == ax:
                try:
                    x = event.xdata
                    if x is None:
                        return
                    
                    dates = mdates.date2num(data.index)
                    idx = (np.abs(dates - x)).argmin()
                    row = data.iloc[idx]
                    date = data.index[idx]
                    
                    # Remove old tooltip
                    if self.tooltip_text:
                        self.tooltip_text.remove()
                    
                    # Rich tooltip
                    tooltip = f"📅 {date.strftime('%Y-%m-%d')}\n"
                    tooltip += f"💲 Open: ${row['Open']:.2f}\n"
                    tooltip += f"   High: ${row['High']:.2f}\n"
                    tooltip += f"   Low: ${row['Low']:.2f}\n"
                    tooltip += f"   Close: ${row['Close']:.2f}\n"
                    tooltip += f"📊 Volume: {row['Volume']/1e6:.2f}M\n"
                    if pd.notna(row.get('RSI')):
                        tooltip += f"📈 RSI: {row['RSI']:.1f}\n"
                    if pd.notna(row.get('MACD')):
                        tooltip += f"⚡ MACD: {row['MACD']:.3f}"
                    
                    self.tooltip_text = ax.text(0.02, 0.98, tooltip,
                                               transform=ax.transAxes,
                                               bbox=dict(boxstyle='round,pad=1',
                                                        facecolor=self.colors['sidebar'],
                                                        edgecolor=self.colors['accent'],
                                                        linewidth=2, alpha=0.95),
                                               color=self.colors['text'],
                                               fontsize=10,
                                               verticalalignment='top',
                                               fontfamily='monospace',
                                               fontweight='bold')
                    canvas.draw_idle()
                except:
                    pass
        
        def on_leave(event):
            if self.tooltip_text:
                self.tooltip_text.remove()
                self.tooltip_text = None
                canvas.draw_idle()
        
        canvas.mpl_connect('motion_notify_event', on_hover)
        canvas.mpl_connect('axes_leave_event', on_leave)
    
    def plot_candlesticks(self, ax, data):
        width = 0.6
        for idx in range(len(data)):
            date = mdates.date2num(data.index[idx])
            open_p = data['Open'].iloc[idx]
            close_p = data['Close'].iloc[idx]
            high = data['High'].iloc[idx]
            low = data['Low'].iloc[idx]
            
            color = self.colors['success'] if close_p >= open_p else self.colors['danger']
            
            ax.plot([date, date], [low, high], color=color, linewidth=1.2, alpha=0.9, zorder=3)
            
            height = abs(close_p - open_p)
            if height < 0.001:
                height = 0.001
            bottom = min(open_p, close_p)
            
            rect = Rectangle((date - width/2, bottom), width, height,
                           facecolor=color, edgecolor=color, alpha=0.95, zorder=3)
            ax.add_patch(rect)
    
    def show_analysis(self, data, ticker, stock):
        """Show comprehensive analysis with AI insight"""
        current_price = data['Close'].iloc[-1]
        prev_price = data['Close'].iloc[-2]
        change = ((current_price - prev_price) / prev_price) * 100
        
        ma20 = data['MA_20'].iloc[-1]
        ma50 = data['MA_50'].iloc[-1]
        rsi = data['RSI'].iloc[-1]
        macd = data['MACD'].iloc[-1]
        macd_signal = data['MACD_Signal'].iloc[-1]
        
        # Get info
        try:
            info = stock.info
            name = info.get('longName', ticker)
            market_cap = info.get('marketCap', 0)
            sector = info.get('sector', 'N/A')
        except:
            name = ticker
            market_cap = 0
            sector = 'N/A'
        
        # Stock info
        info_text = f"{'='*42}\n{ticker} - {name}\n{'='*42}\n\n"
        info_text += f"Sector: {sector}\n"
        if market_cap > 1e9:
            info_text += f"Market Cap: ${market_cap/1e9:.1f}B\n"
        info_text += f"\nPrice: ${current_price:.2f}\n"
        info_text += f"Change: {change:+.2f}%\n\n"
        info_text += f"MA-{self.ma20_period.get()}: ${ma20:.2f}\n"
        info_text += f"MA-{self.ma50_period.get()}: ${ma50:.2f}\n"
        info_text += f"\nRSI: {rsi:.1f}\n"
        info_text += f"MACD: {macd:.3f}\n"
        
        self.info_text.insert(tk.END, info_text)
        
        # AI INSIGHT - Dynamic generation
        insights = []
        trend = "neutral"
        
        if pd.notna(ma20) and pd.notna(ma50):
            if ma20 > ma50 and current_price > ma20:
                trend = "bullish"
                insights.append(f"{ticker} is in a short-term bullish trend with price trading above both {self.ma20_period.get()}- and {self.ma50_period.get()}-day moving averages.")
            elif ma20 < ma50 and current_price < ma20:
                trend = "bearish"
                insights.append(f"{ticker} shows bearish signals with price below key moving averages, indicating potential downward pressure.")
            else:
                insights.append(f"{ticker} is in a transitional phase with mixed moving average signals.")
        
        if rsi > 70:
            insights.append(f"RSI indicates overbought conditions ({rsi:.1f}), suggesting potential consolidation or pullback ahead.")
        elif rsi < 30:
            insights.append(f"RSI shows oversold territory ({rsi:.1f}), which may present a buying opportunity if other indicators confirm.")
        else:
            insights.append(f"RSI indicates moderate momentum ({rsi:.1f}), suggesting balanced market conditions.")
        
        if macd > macd_signal:
            insights.append("MACD crossover supports continued upward movement with positive momentum.")
        else:
            insights.append("MACD signals weakening momentum with bearish crossover pattern.")
        
        # Volume analysis
        current_vol = data['Volume'].iloc[-1]
        avg_vol = data['Volume_MA'].iloc[-1]
        if current_vol > avg_vol * 1.5:
            insights.append("Strong volume confirms the current price action.")
        
        # Generate summary
        ai_summary = "🤖 AI Market Insight\n"
        ai_summary += "="*42 + "\n\n"
        ai_summary += "\n\n".join(insights)
        
        # Add resistance/support levels
        bb_upper = data['BB_Upper'].iloc[-1]
        bb_lower = data['BB_Lower'].iloc[-1]
        ai_summary += f"\n\n📍 Key Levels:\n"
        ai_summary += f"   Resistance: ${bb_upper:.2f}\n"
        ai_summary += f"   Support: ${bb_lower:.2f}\n"
        ai_summary += f"   Current distance from resistance: {((bb_upper - current_price)/current_price*100):.1f}%"
        
        self.insight_text.insert(tk.END, ai_summary)
        
        # Signals (keeping existing logic)
        signals = "MOVING AVERAGES\n" + "-"*42 + "\n"
        score = 0
        
        if pd.notna(ma20) and pd.notna(ma50):
            if ma20 > ma50:
                signals += "🟢 Bullish Crossover\n"
                signals += f"   {self.ma20_period.get()}-MA > {self.ma50_period.get()}-MA\n"
                score += 2
            else:
                signals += "🔴 Bearish Crossover\n"
                score -= 2
        
        if current_price > ma20:
            signals += f"🟢 Price above {self.ma20_period.get()}-MA\n"
            score += 1
        else:
            signals += f"🔴 Price below {self.ma20_period.get()}-MA\n"
            score -= 1
        
        signals += "\nRSI\n" + "-"*42 + "\n"
        if rsi > 70:
            signals += f"🔴 Overbought ({rsi:.1f})\n"
            score -= 1
        elif rsi < 30:
            signals += f"🟢 Oversold ({rsi:.1f})\n"
            score += 2
        else:
            signals += f"⚪ Neutral ({rsi:.1f})\n"
        
        signals += "\nMACD\n" + "-"*42 + "\n"
        if macd > macd_signal:
            signals += "🟢 Bullish MACD\n"
            score += 2
        else:
            signals += "🔴 Bearish MACD\n"
            score -= 2
        
        signals += f"\n{'='*42}\n"
        signals += f"SCORE: {score}\n"
        signals += f"{'='*42}"
        
        self.signals_text.insert(tk.END, signals)
        
        # Recommendation
        for widget in self.rec_frame.winfo_children():
            widget.destroy()
        
        rec_inner = tk.Frame(self.rec_frame, bg=self.colors['card'])
        rec_inner.pack(fill=tk.BOTH, expand=True, pady=18)
        
        if score >= 5:
            rec = "🚀 STRONG BUY"
            rec_color = self.colors['success']
            desc = "Multiple bullish indicators aligned"
        elif score >= 2:
            rec = "📈 BUY"
            rec_color = self.colors['success']
            desc = "Positive momentum detected"
        elif score >= -1:
            rec = "⚪ HOLD"
            rec_color = self.colors['warning']
            desc = "Mixed signals - wait for clarity"
        elif score >= -4:
            rec = "📉 SELL"
            rec_color = self.colors['danger']
            desc = "Bearish signals dominating"
        else:
            rec = "🔻 STRONG SELL"
            rec_color = self.colors['danger']
            desc = "Multiple bearish indicators"
        
        tk.Label(rec_inner, text=rec, font=('Arial', 19, 'bold'),
                fg=rec_color, bg=self.colors['card']).pack(pady=(0,12))
        
        tk.Label(rec_inner, text=desc, font=('Arial', 10),
                fg=self.colors['text'], bg=self.colors['card']).pack()
    
    def show_watchlist(self):
        """Enhanced watchlist with icons"""
        win = tk.Toplevel(self.root)
        win.title("⭐ Watchlist")
        win.geometry("550x650")
        win.configure(bg=self.colors['bg'])
        
        header = tk.Frame(win, bg=self.colors['card'], height=75)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="⭐ My Watchlist", font=('Arial', 15, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT, 
                                                                      pady=28, padx=28)
        
        tk.Button(header, text="+ Add",
                 command=lambda: self.quick_add_to_watchlist(win),
                 font=('Arial', 10, 'bold'), bg=self.colors['accent'],
                 fg='white', bd=0, padx=18, pady=9,
                 cursor='hand2').pack(side=tk.RIGHT, padx=28, pady=22)
        
        tk.Frame(header, bg=self.colors['border'], height=1).pack(side=tk.BOTTOM, fill=tk.X)
        
        content_frame = tk.Frame(win, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(content_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])
        
        scrollable_frame.bind("<Configure>",
                             lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=22, pady=22)
        scrollbar.pack(side="right", fill="y", pady=22)
        
        stocks = self.watchlist.get('stocks', [])
        if not stocks:
            tk.Label(scrollable_frame, 
                    text="No stocks yet\n\nClick '+ Add' to get started",
                    font=('Arial', 12), fg=self.colors['text_dim'],
                    bg=self.colors['bg'], justify=tk.CENTER).pack(expand=True, pady=60)
        else:
            for ticker in stocks:
                self.create_watchlist_card_ultra(scrollable_frame, ticker, win)
    
    def create_watchlist_card_ultra(self, parent, ticker, window):
        card = tk.Frame(parent, bg=self.colors['card'],
                       highlightbackground=self.colors['border'],
                       highlightthickness=1)
        card.pack(fill=tk.X, pady=6)
        
        inner = tk.Frame(card, bg=self.colors['card'])
        inner.pack(fill=tk.X, padx=22, pady=16)
        
        # Ticker with star icon
        left = tk.Frame(inner, bg=self.colors['card'])
        left.pack(side=tk.LEFT)
        
        tk.Label(left, text="⭐", font=('Arial', 14),
                fg=self.colors['warning'], bg=self.colors['card']).pack(side=tk.LEFT, padx=(0,8))
        
        tk.Label(left, text=ticker, font=('Arial', 14, 'bold'),
                fg=self.colors['text'], bg=self.colors['card']).pack(side=tk.LEFT)
        
        # Check if has alert
        if ticker in self.alerts:
            tk.Label(left, text="🔔", font=('Arial', 12),
                    fg=self.colors['danger'], bg=self.colors['card']).pack(side=tk.LEFT, padx=8)
        
        # Buttons
        btn_frame = tk.Frame(inner, bg=self.colors['card'])
        btn_frame.pack(side=tk.RIGHT)
        
        tk.Button(btn_frame, text="📊",
                 command=lambda: [window.destroy(), self.quick_analyze(ticker)],
                 font=('Arial', 14), bg=self.colors['accent'],
                 fg='white', bd=0, padx=12, pady=6,
                 cursor='hand2').pack(side=tk.LEFT, padx=3)
        
        tk.Button(btn_frame, text="🗑️",
                 command=lambda: self.remove_from_watchlist_ultra(ticker, card),
                 font=('Arial', 14), bg=self.colors['danger'],
                 fg='white', bd=0, padx=12, pady=6,
                 cursor='hand2').pack(side=tk.LEFT, padx=3)
    
    def quick_add_to_watchlist(self, parent_win):
        dialog = tk.Toplevel(parent_win)
        dialog.title("Add to Watchlist")
        dialog.geometry("320x160")
        dialog.configure(bg=self.colors['bg'])
        dialog.resizable(False, False)
        
        tk.Label(dialog, text="Enter ticker:",
                font=('Arial', 11), fg=self.colors['text'],
                bg=self.colors['bg']).pack(pady=(22,12))
        
        entry = tk.Entry(dialog, font=('Arial', 12), width=16,
                        bg=self.colors['card'], fg=self.colors['text'],
                        insertbackground=self.colors['accent'], bd=1, relief='solid')
        entry.pack(pady=12)
        entry.focus()
        
        def add_it():
            ticker = entry.get().strip().upper()
            stocks = self.watchlist.get('stocks', [])
            if ticker and ticker not in stocks:
                stocks.append(ticker)
                self.watchlist['stocks'] = stocks
                self.save_watchlist()
                dialog.destroy()
                parent_win.destroy()
                self.show_watchlist()
            elif ticker in stocks:
                messagebox.showinfo("Already Added", f"{ticker} is already in watchlist")
        
        entry.bind('<Return>', lambda e: add_it())
        
        tk.Button(dialog, text="Add", command=add_it,
                 font=('Arial', 11, 'bold'), bg=self.colors['accent'],
                 fg='white', bd=0, padx=22, pady=9,
                 cursor='hand2').pack(pady=12)
    
    def add_to_watchlist(self):
        if self.current_ticker:
            stocks = self.watchlist.get('stocks', [])
            if self.current_ticker not in stocks:
                stocks.append(self.current_ticker)
                self.watchlist['stocks'] = stocks
                self.save_watchlist()
                messagebox.showinfo("Added", f"{self.current_ticker} added!")
                self.add_watchlist_btn.config(text="✓ Added", state='disabled')
    
    def remove_from_watchlist_ultra(self, ticker, card_widget):
        stocks = self.watchlist.get('stocks', [])
        if ticker in stocks:
            stocks.remove(ticker)
            self.watchlist['stocks'] = stocks
            self.save_watchlist()
            card_widget.destroy()
    
    def set_alert(self):
        if not self.current_ticker:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("🔔 Set Alert")
        dialog.geometry("360x270")
        dialog.configure(bg=self.colors['bg'])
        dialog.resizable(False, False)
        
        tk.Label(dialog, text=f"Set Alert for {self.current_ticker}",
                font=('Arial', 13, 'bold'), fg=self.colors['text'],
                bg=self.colors['bg']).pack(pady=22)
        
        tk.Label(dialog, text="Alert when price goes:",
                font=('Arial', 10), fg=self.colors['text'],
                bg=self.colors['bg']).pack()
        
        alert_type = tk.StringVar(value="above")
        
        tk.Radiobutton(dialog, text="Above", variable=alert_type, value="above",
                      font=('Arial', 10), bg=self.colors['bg'], fg=self.colors['text'],
                      selectcolor=self.colors['card']).pack()
        
        tk.Radiobutton(dialog, text="Below", variable=alert_type, value="below",
                      font=('Arial', 10), bg=self.colors['bg'], fg=self.colors['text'],
                      selectcolor=self.colors['card']).pack()
        
        tk.Label(dialog, text="Target price:",
                font=('Arial', 10), fg=self.colors['text'],
                bg=self.colors['bg']).pack(pady=(12,6))
        
        price_entry = tk.Entry(dialog, font=('Arial', 11), width=16,
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
                # Add to watchlist alerts list
                alerts_list = self.watchlist.get('alerts', [])
                if self.current_ticker not in alerts_list:
                    alerts_list.append(self.current_ticker)
                    self.watchlist['alerts'] = alerts_list
                    self.save_watchlist()
                messagebox.showinfo("Alert Set", 
                                  f"Alert set for {self.current_ticker} {alert_type.get()} ${price:.2f}")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Invalid", "Enter a valid number")
        
        tk.Button(dialog, text="Set Alert", command=save_alert,
                 font=('Arial', 11, 'bold'), bg=self.colors['accent'],
                 fg='white', bd=0, padx=22, pady=10,
                 cursor='hand2').pack(pady=22)
    
    def export_menu(self):
        if not self.current_ticker:
            messagebox.showwarning("No Data", "Analyze a stock first!")
            return
        
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="📊 Chart (PNG)", command=self.export_chart_png)
        menu.add_command(label="📄 Analysis (TXT)", command=self.export_analysis_txt)
        menu.add_command(label="📑 Data (CSV)", command=self.export_data_csv)
        
        menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
    
    def export_chart_png(self):
        if not hasattr(self, 'current_canvas') or not self.current_ticker:
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=f"{self.current_ticker}_{datetime.now().strftime('%Y%m%d')}.png",
            filetypes=[("PNG", "*.png"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                self.current_canvas.figure.savefig(filename, dpi=300,
                                                   bbox_inches='tight',
                                                   facecolor=self.colors['card'])
                messagebox.showinfo("Success", "Chart exported!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed:\n{str(e)}")
    
    def export_analysis_txt(self):
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
                    f.write(f"Stock Analysis - {self.current_ticker}\n")
                    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("="*60 + "\n\n")
                    f.write("STOCK INFO\n" + "-"*60 + "\n")
                    f.write(self.info_text.get(1.0, tk.END))
                    f.write("\nAI INSIGHT\n" + "-"*60 + "\n")
                    f.write(self.insight_text.get(1.0, tk.END))
                    f.write("\nSIGNALS\n" + "-"*60 + "\n")
                    f.write(self.signals_text.get(1.0, tk.END))
                messagebox.showinfo("Success", "Analysis exported!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed:\n{str(e)}")
    
    def export_data_csv(self):
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
                messagebox.showinfo("Success", "Data exported!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = StockAnalyzerUltra(root)
    root.mainloop()
