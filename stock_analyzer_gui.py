import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

class StockAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Analyzer Pro - TradingView Style")
        self.root.geometry("1600x1000")
# Try to set window icon
try:
    self.root.iconphoto(False, tk.PhotoImage(file='stock_analyzer_icon.png'))
except:
    pass  # Icon file not found, continue without icon
        
        # TradingView inspired color scheme
        self.colors = {
            'primary_bg': '#131722',        # TradingView dark blue
            'secondary_bg': '#1E222D',      # Darker panels
            'accent': '#2962FF',            # TradingView blue
            'accent_orange': '#FF6D00',     # Orange accent
            'light_blue': '#42A5F5',       # Light blue
            'dark_blue': '#1565C0',        # Dark blue
            'text_primary': '#D1D4DC',     # Light gray text
            'text_secondary': '#B2B5BE',   # Medium gray text
            'button_bg': '#2962FF',        # Blue buttons
            'button_hover': '#1E88E5',     # Lighter blue on hover
            'entry_bg': '#2A2E39',         # Dark entry background
            'chart_bg': '#0D1421',         # Very dark chart background
            'grid_color': '#2A2E39',       # Grid lines
            'success': '#4CAF50',          # Green
            'warning': '#FF9800',          # Orange
            'danger': '#F44336'            # Red
        }
        
        # Set overall background
        root.configure(bg=self.colors['primary_bg'])
        
        # Create main frame
        main_frame = tk.Frame(root, bg=self.colors['primary_bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create top toolbar
        self.create_toolbar(main_frame)
        
        # Create main content area
        self.create_content_area(main_frame)
        
        # Bind Enter key to analyze
        self.ticker_entry.bind('<Return>', lambda event: self.analyze_stock())
        
        # Add welcome message
        self.add_welcome_message()

    def create_toolbar(self, parent):
        """Create TradingView style toolbar"""
        toolbar = tk.Frame(parent, bg=self.colors['secondary_bg'], height=60)
        toolbar.pack(fill=tk.X, padx=0, pady=(0, 5))
        toolbar.pack_propagate(False)
        
        # Left side - Logo and title
        left_frame = tk.Frame(toolbar, bg=self.colors['secondary_bg'])
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=10)
        
        title = tk.Label(left_frame, text="📈 STOCK ANALYZER PRO", 
                        font=('Segoe UI', 14, 'bold'),
                        fg=self.colors['accent'],
                        bg=self.colors['secondary_bg'])
        title.pack(side=tk.LEFT)
        
        # Center - Search area
        center_frame = tk.Frame(toolbar, bg=self.colors['secondary_bg'])
        center_frame.pack(side=tk.LEFT, expand=True, fill=tk.Y, padx=20, pady=12)
        
        # Search container
        search_container = tk.Frame(center_frame, bg=self.colors['entry_bg'], 
                                   relief='solid', bd=1)
        search_container.pack(side=tk.LEFT, padx=(50, 0))
        
        # Search icon
        search_icon = tk.Label(search_container, text="🔍", 
                              font=('Segoe UI', 12),
                              fg=self.colors['text_secondary'],
                              bg=self.colors['entry_bg'])
        search_icon.pack(side=tk.LEFT, padx=(8, 5), pady=8)
        
        # Ticker entry
        self.ticker_var = tk.StringVar()
        self.ticker_entry = tk.Entry(search_container, 
                                    textvariable=self.ticker_var,
                                    font=('Segoe UI', 11),
                                    bg=self.colors['entry_bg'],
                                    fg=self.colors['text_primary'],
                                    bd=0,
                                    width=15,
                                    insertbackground=self.colors['accent'])
        self.ticker_entry.pack(side=tk.LEFT, pady=8)
        
        # Analyze button
        self.analyze_btn = tk.Button(search_container,
                                    text="ANALYZE",
                                    command=self.analyze_stock,
                                    font=('Segoe UI', 10, 'bold'),
                                    bg=self.colors['button_bg'],
                                    fg=self.colors['text_primary'],
                                    bd=0,
                                    padx=15,
                                    pady=8,
                                    activebackground=self.colors['button_hover'],
                                    cursor='hand2')
        self.analyze_btn.pack(side=tk.LEFT, padx=(5, 8))
        
        # Right side - Progress
        right_frame = tk.Frame(toolbar, bg=self.colors['secondary_bg'])
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=15, pady=15)
        
        self.progress = ttk.Progressbar(right_frame, mode='indeterminate', length=150)
        self.progress.pack(side=tk.RIGHT)

    def create_content_area(self, parent):
        """Create TradingView style content area"""
        content_frame = tk.Frame(parent, bg=self.colors['primary_bg'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left sidebar - Analysis panel
        left_panel = tk.Frame(content_frame, bg=self.colors['secondary_bg'], width=320)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_panel.pack_propagate(False)
        
        # Analysis header
        analysis_header = tk.Frame(left_panel, bg=self.colors['secondary_bg'], height=40)
        analysis_header.pack(fill=tk.X, padx=10, pady=(10, 0))
        analysis_header.pack_propagate(False)
        
        analysis_title = tk.Label(analysis_header, text="📊 Technical Analysis",
                                 font=('Segoe UI', 12, 'bold'),
                                 fg=self.colors['text_primary'],
                                 bg=self.colors['secondary_bg'])
        analysis_title.pack(side=tk.LEFT, pady=10)
        
        # Analysis content
        analysis_content = tk.Frame(left_panel, bg=self.colors['secondary_bg'])
        analysis_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Results text area
        self.results_text = tk.Text(analysis_content,
                                   bg=self.colors['primary_bg'],
                                   fg=self.colors['text_primary'],
                                   font=('Consolas', 9),
                                   bd=0,
                                   wrap=tk.WORD,
                                   selectbackground=self.colors['accent'],
                                   insertbackground=self.colors['accent'])
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Right panel - Chart area
        right_panel = tk.Frame(content_frame, bg=self.colors['secondary_bg'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Chart header
        chart_header = tk.Frame(right_panel, bg=self.colors['secondary_bg'], height=40)
        chart_header.pack(fill=tk.X, padx=10, pady=(10, 0))
        chart_header.pack_propagate(False)
        
        chart_title = tk.Label(chart_header, text="📈 Price Chart",
                              font=('Segoe UI', 12, 'bold'),
                              fg=self.colors['text_primary'],
                              bg=self.colors['secondary_bg'])
        chart_title.pack(side=tk.LEFT, pady=10)
        
        # Chart indicators
        indicators_frame = tk.Frame(chart_header, bg=self.colors['secondary_bg'])
        indicators_frame.pack(side=tk.RIGHT, pady=10)
        
        # MA indicators
        ma20_label = tk.Label(indicators_frame, text="● 20-MA", 
                             font=('Segoe UI', 9), fg='#FF6B35',
                             bg=self.colors['secondary_bg'])
        ma20_label.pack(side=tk.RIGHT, padx=5)
        
        ma50_label = tk.Label(indicators_frame, text="● 50-MA", 
                             font=('Segoe UI', 9), fg='#F7931E',
                             bg=self.colors['secondary_bg'])
        ma50_label.pack(side=tk.RIGHT, padx=5)
        
        # Chart container with scrollbars
        chart_container = tk.Frame(right_panel, bg=self.colors['chart_bg'])
        chart_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create canvas for scrolling
        self.chart_canvas = tk.Canvas(chart_container, 
                                     bg=self.colors['chart_bg'],
                                     highlightthickness=0)
        
        # Create scrollbars
        h_scrollbar = ttk.Scrollbar(chart_container, orient=tk.HORIZONTAL, 
                                   command=self.chart_canvas.xview)
        v_scrollbar = ttk.Scrollbar(chart_container, orient=tk.VERTICAL, 
                                   command=self.chart_canvas.yview)
        
        # Configure canvas scrolling
        self.chart_canvas.configure(xscrollcommand=h_scrollbar.set,
                                   yscrollcommand=v_scrollbar.set)
        
        # Pack scrollbars and canvas
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chart_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create frame inside canvas for charts
        self.chart_frame = tk.Frame(self.chart_canvas, bg=self.colors['chart_bg'])
        self.chart_window = self.chart_canvas.create_window(0, 0, anchor='nw', window=self.chart_frame)
        
        # Bind canvas events
        self.chart_frame.bind('<Configure>', self.on_frame_configure)
        self.chart_canvas.bind('<Configure>', self.on_canvas_configure)
        self.chart_canvas.bind('<Button-4>', self.on_mousewheel)
        self.chart_canvas.bind('<Button-5>', self.on_mousewheel)
        self.chart_canvas.bind('<MouseWheel>', self.on_mousewheel)

    def on_frame_configure(self, event):
        """Update scrollregion when frame size changes"""
        self.chart_canvas.configure(scrollregion=self.chart_canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        """Update frame width when canvas size changes"""
        canvas_width = event.width
        self.chart_canvas.itemconfig(self.chart_window, width=canvas_width)
    
    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if event.num == 4 or event.delta > 0:
            self.chart_canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.chart_canvas.yview_scroll(1, "units")

    def add_welcome_message(self):
        """Add TradingView style welcome message"""
        welcome_msg = """
📈 STOCK ANALYZER PRO
═══════════════════════

🎯 Professional Trading Tools:
  • Real-time market data
  • Interactive crosshair analysis
  • Technical indicators (MA, RSI)
  • Smart trading signals
  • TradingView-style interface

💡 Quick Start:
  1. Enter ticker symbol (AAPL, GOOGL, TSLA...)
  2. Press ENTER or click ANALYZE
  3. Hover over charts for detailed info

🚀 Ready to analyze the markets!

═══════════════════════
        """
        
        self.results_text.insert(tk.END, welcome_msg)
        self.results_text.config(state='disabled')

    def calculate_rsi(self, prices, window=14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def analyze_stock(self):
        ticker = self.ticker_var.get().strip().upper()
        
        if not ticker:
            messagebox.showwarning("Input Required", "Please enter a stock ticker symbol!")
            return
        
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        
        self.progress.start()
        self.analyze_btn.config(state='disabled', text="ANALYZING...", 
                               bg=self.colors['warning'])
        
        thread = threading.Thread(target=self.run_analysis, args=(ticker,))
        thread.daemon = True
        thread.start()

    def run_analysis(self, ticker):
        try:
            self.root.after(0, lambda: self.update_text(f"🔍 Fetching market data for {ticker}...\n\n"))
            
            stock = yf.Ticker(ticker)
            data = stock.history(period="6mo")
            
            if data.empty:
                self.root.after(0, lambda: self.update_text(f"❌ No data found for {ticker}.\nPlease verify the ticker symbol.\n"))
                return
            
            data['MA_20'] = data['Close'].rolling(window=20).mean()
            data['MA_50'] = data['Close'].rolling(window=50).mean()
            data['RSI'] = self.calculate_rsi(data['Close'])
            
            self.root.after(0, lambda: self.create_tradingview_chart(data, ticker))
            self.root.after(0, lambda: self.display_analysis(data, ticker))
            
        except Exception as e:
            self.root.after(0, lambda: self.update_text(f"❌ Error: {str(e)}\n"))
        
        finally:
            self.root.after(0, self.stop_progress)

    def create_tradingview_chart(self, data, ticker):
        """Create TradingView style charts with floating info tooltips"""
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        # Set TradingView style
        plt.style.use('dark_background')
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(18, 12), height_ratios=[3, 1])
        fig.patch.set_facecolor(self.colors['chart_bg'])
        
        # Store data for crosshair functionality
        self.chart_data = data
        self.ticker_name = ticker
        
        # Price chart styling
        ax1.plot(data.index, data['Close'], linewidth=2.5, 
                label=f'{ticker}', color='#00E676', alpha=0.9)
        ax1.plot(data.index, data['MA_20'], linewidth=2, 
                label='MA20', color='#FF6B35', alpha=0.8)
        ax1.plot(data.index, data['MA_50'], linewidth=2, 
                label='MA50', color='#F7931E', alpha=0.8)
        
        # TradingView style chart formatting
        ax1.set_facecolor(self.colors['chart_bg'])
        ax1.set_title(f'{ticker} • 6M • Technical Analysis', 
                     color=self.colors['text_primary'], fontsize=16, 
                     fontweight='bold', pad=20, loc='left')
        ax1.set_ylabel('Price (USD)', color=self.colors['text_primary'], 
                      fontsize=11, fontweight='500')
        ax1.grid(True, alpha=0.1, color=self.colors['text_secondary'])
        ax1.tick_params(colors=self.colors['text_secondary'], labelsize=9)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_color(self.colors['grid_color'])
        ax1.spines['bottom'].set_color(self.colors['grid_color'])
        
        # Price legend
        legend1 = ax1.legend(loc='upper left', fontsize=10, frameon=False)
        for text in legend1.get_texts():
            text.set_color(self.colors['text_primary'])
        
        # RSI chart styling
        ax2.plot(data.index, data['RSI'], linewidth=2.5, 
                label='RSI(14)', color='#BB86FC', alpha=0.9)
        ax2.axhline(y=70, color='#FF5252', linestyle='--', alpha=0.6, linewidth=1.5)
        ax2.axhline(y=30, color='#4CAF50', linestyle='--', alpha=0.6, linewidth=1.5)
        ax2.fill_between(data.index, 70, 100, alpha=0.1, color='#FF5252')
        ax2.fill_between(data.index, 0, 30, alpha=0.1, color='#4CAF50')
        
        ax2.set_facecolor(self.colors['chart_bg'])
        ax2.set_ylabel('RSI', color=self.colors['text_primary'], 
                      fontsize=11, fontweight='500')
        ax2.set_xlabel('Date', color=self.colors['text_primary'], 
                      fontsize=11, fontweight='500')
        ax2.set_ylim(0, 100)
        ax2.grid(True, alpha=0.1, color=self.colors['text_secondary'])
        ax2.tick_params(colors=self.colors['text_secondary'], labelsize=9)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_color(self.colors['grid_color'])
        ax2.spines['bottom'].set_color(self.colors['grid_color'])
        
        # RSI legend
        legend2 = ax2.legend(loc='upper left', fontsize=9, frameon=False)
        for text in legend2.get_texts():
            text.set_color(self.colors['text_primary'])
        
        # Current price annotation
        current_price = data['Close'].iloc[-1]
        ax1.annotate(f'${current_price:.2f}', 
                    xy=(data.index[-1], current_price),
                    xytext=(15, 0), textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#00E676', 
                             alpha=0.8, edgecolor='none'),
                    color='black', fontweight='bold', fontsize=10)
        
        # Create crosshair elements (initially invisible)
        self.vline1 = ax1.axvline(x=data.index[0], color='#FFD700', 
                                 linestyle='-', alpha=0.8, linewidth=1, visible=False)
        self.hline1 = ax1.axhline(y=current_price, color='#FFD700', 
                                 linestyle='-', alpha=0.8, linewidth=1, visible=False)
        self.vline2 = ax2.axvline(x=data.index[0], color='#FFD700', 
                                 linestyle='-', alpha=0.8, linewidth=1, visible=False)
        self.hline2 = ax2.axhline(y=50, color='#FFD700', 
                                 linestyle='-', alpha=0.8, linewidth=1, visible=False)
        
        # Create crosshair dots
        self.dot1, = ax1.plot([], [], 'o', color='#FFD700', markersize=6, 
                             alpha=0.9, visible=False, markeredgecolor='white', 
                             markeredgewidth=1)
        self.dot2, = ax2.plot([], [], 'o', color='#FFD700', markersize=6, 
                             alpha=0.9, visible=False, markeredgecolor='white', 
                             markeredgewidth=1)
        
        # Create floating info boxes (initially invisible)
        self.info_box1 = None
        self.info_box2 = None
        
        # Store axes and figure
        self.ax1 = ax1
        self.ax2 = ax2
        
        plt.tight_layout()
        plt.subplots_adjust(hspace=0.15)
        
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Connect mouse events
        canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        canvas.mpl_connect('axes_enter_event', self.on_mouse_enter)
        canvas.mpl_connect('axes_leave_event', self.on_mouse_leave)
        
        # Update scroll region
        self.chart_frame.update_idletasks()
        self.chart_canvas.configure(scrollregion=self.chart_canvas.bbox("all"))
        
        self.current_canvas = canvas
        self.current_fig = fig

    def on_mouse_move(self, event):
        """Handle mouse movement for floating crosshair tooltips"""
        if event.inaxes is None:
            return
        
        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return
        
        try:
            # Convert x coordinate to datetime
            x_datetime = matplotlib.dates.num2date(x)
            
            # Find closest data point
            closest_idx = None
            min_distance = float('inf')
            
            for i, date in enumerate(self.chart_data.index):
                distance = abs((date - x_datetime.replace(tzinfo=date.tzinfo)).total_seconds())
                if distance < min_distance:
                    min_distance = distance
                    closest_idx = i
            
            if closest_idx is not None:
                closest_date = self.chart_data.index[closest_idx]
                closest_data = self.chart_data.iloc[closest_idx]
                
                # Calculate metrics
                price = closest_data['Close']
                ma20 = closest_data['MA_20']
                ma50 = closest_data['MA_50']
                
                # Price change
                if closest_idx > 0:
                    prev_price = self.chart_data.iloc[closest_idx - 1]['Close']
                    price_change = price - prev_price
                    price_change_pct = (price_change / prev_price) * 100
                else:
                    price_change = 0
                    price_change_pct = 0
                
                # Update crosshair lines
                self.vline1.set_xdata([closest_date, closest_date])
                self.vline2.set_xdata([closest_date, closest_date])
                self.vline1.set_visible(True)
                self.vline2.set_visible(True)
                
                if event.inaxes == self.ax1:
                    # Price chart
                    self.hline1.set_ydata([y, y])
                    self.hline1.set_visible(True)
                    self.dot1.set_data([closest_date], [price])
                    self.dot1.set_visible(True)
                    
                    # Remove previous info box
                    if self.info_box1:
                        self.info_box1.remove()
                    
                    # Create floating info box near cursor
                    info_text = f"{closest_date.strftime('%m/%d/%Y')}\n"
                    info_text += f"💰 ${price:.2f}\n"
                    
                    change_symbol = "+" if price_change >= 0 else ""
                    info_text += f"📈 {change_symbol}{price_change:.2f} ({price_change_pct:+.1f}%)\n"
                    
                    if pd.notna(ma20):
                        ma20_diff = ((price - ma20) / ma20) * 100
                        ma20_status = "↑" if price > ma20 else "↓"
                        info_text += f"📊 MA20: {ma20_status} {abs(ma20_diff):.1f}%\n"
                    
                    if pd.notna(ma50):
                        ma50_diff = ((price - ma50) / ma50) * 100
                        ma50_status = "↑" if price > ma50 else "↓"
                        info_text += f"📈 MA50: {ma50_status} {abs(ma50_diff):.1f}%"
                    
                    # Position tooltip near cursor
                    self.info_box1 = self.ax1.text(x_datetime, y, info_text,
                                                  bbox=dict(boxstyle='round,pad=0.8', 
                                                           facecolor='#1E1E1E', 
                                                           edgecolor='#FFD700',
                                                           alpha=0.95),
                                                  color='#FFFFFF', fontsize=8,
                                                  fontfamily='monospace',
                                                  verticalalignment='bottom',
                                                  horizontalalignment='left')
                
                elif event.inaxes == self.ax2:
                    # RSI chart
                    self.hline2.set_ydata([y, y])
                    self.hline2.set_visible(True)
                    self.dot2.set_data([closest_date], [closest_data['RSI']])
                    self.dot2.set_visible(True)
                    
                    # Remove previous info box
                    if self.info_box2:
                        self.info_box2.remove()
                    
                    rsi_current = closest_data['RSI']
                    
                    # RSI trend
                    if closest_idx >= 3:
                        rsi_3_ago = self.chart_data.iloc[closest_idx - 3]['RSI']
                        rsi_trend = rsi_current - rsi_3_ago
                        trend_arrow = "📈" if rsi_trend > 2 else "📉" if rsi_trend < -2 else "➡️"
                    else:
                        trend_arrow = "➡️"
                    
                    info_text = f"{closest_date.strftime('%m/%d/%Y')}\n"
                    info_text += f"⚡ RSI: {rsi_current:.1f}\n"
                    info_text += f"📊 Trend: {trend_arrow}\n"
                    
                    if rsi_current > 70:
                        info_text += "🔴 OVERBOUGHT"
                    elif rsi_current < 30:
                        info_text += "🟢 OVERSOLD"
                    elif rsi_current > 50:
                        info_text += "🟡 BULLISH"
                    else:
                        info_text += "🟠 BEARISH"
                    
                    # Position tooltip near cursor
                    self.info_box2 = self.ax2.text(x_datetime, y, info_text,
                                                  bbox=dict(boxstyle='round,pad=0.8', 
                                                           facecolor='#1E1E1E', 
                                                           edgecolor='#FFD700',
                                                           alpha=0.95),
                                                  color='#FFFFFF', fontsize=8,
                                                  fontfamily='monospace',
                                                  verticalalignment='bottom',
                                                  horizontalalignment='left')
            
            self.current_canvas.draw_idle()
            
        except Exception as e:
            pass

    def on_mouse_enter(self, event):
        """Show crosshair when mouse enters"""
        pass

    def on_mouse_leave(self, event):
        """Hide crosshair when mouse leaves"""
        if hasattr(self, 'vline1'):
            self.vline1.set_visible(False)
            self.hline1.set_visible(False)
            self.vline2.set_visible(False)
            self.hline2.set_visible(False)
            self.dot1.set_visible(False)
            self.dot2.set_visible(False)
            
            # Remove info boxes
            if self.info_box1:
                self.info_box1.remove()
                self.info_box1 = None
            if self.info_box2:
                self.info_box2.remove()
                self.info_box2 = None
            
            if hasattr(self, 'current_canvas'):
                self.current_canvas.draw_idle()

    def update_text(self, message):
        """Update analysis text"""
        self.results_text.insert(tk.END, message)
        self.results_text.see(tk.END)

    def display_analysis(self, data, ticker):
        """Display TradingView style analysis"""
        current_price = data['Close'].iloc[-1]
        current_ma20 = data['MA_20'].iloc[-1]
        current_ma50 = data['MA_50'].iloc[-1]
        current_rsi = data['RSI'].iloc[-1]
        
        # Price change
        prev_price = data['Close'].iloc[-2]
        price_change = current_price - prev_price
        price_change_pct = (price_change / prev_price) * 100
        
        analysis = f"""
[{ticker} ANALYSIS]
=======================

CURRENT METRICS:
  Price: ${current_price:.2f}
  Change: {price_change:+.2f} ({price_change_pct:+.1f}%)
  20-MA: ${current_ma20:.2f}
  50-MA: ${current_ma50:.2f}
  RSI: {current_rsi:.1f}

TECHNICAL SIGNALS:
"""
        
        # Simple, data-driven signals
        if pd.notna(current_ma20) and pd.notna(current_ma50):
            if current_ma20 > current_ma50:
                analysis += "  [+] MA Signal: 20-day above 50-day (Bullish)\n"
            else:
                analysis += "  [-] MA Signal: 20-day below 50-day (Bearish)\n"
        
        # Price vs moving averages
        if pd.notna(current_ma20):
            if current_price > current_ma20:
                analysis += "  [+] Price above 20-day MA (Bullish)\n"
            else:
                analysis += "  [-] Price below 20-day MA (Bearish)\n"
        
        # RSI signals
        if current_rsi > 70:
            analysis += "  [-] RSI Overbought (>70) - Potential selling\n"
        elif current_rsi < 30:
            analysis += "  [+] RSI Oversold (<30) - Potential buying\n"
        else:
            analysis += f"  [=] RSI Normal ({current_rsi:.1f}) - No extreme\n"
        
        # Overall recommendation based on actual conditions
        score = 0
        
        # MA trend
        if pd.notna(current_ma20) and pd.notna(current_ma50) and current_ma20 > current_ma50:
            score += 1
        elif pd.notna(current_ma20) and pd.notna(current_ma50) and current_ma20 < current_ma50:
            score -= 1
        
        # Price position
        if pd.notna(current_ma20) and current_price > current_ma20:
            score += 1
        elif pd.notna(current_ma20) and current_price < current_ma20:
            score -= 1
        
        # RSI condition
        if current_rsi < 30:
            score += 1
        elif current_rsi > 70:
            score -= 1
        
        analysis += f"\nOVERALL RECOMMENDATION:\n"
        if score >= 2:
            analysis += "  [BUY] - Bullish signals dominate\n"
        elif score <= -2:
            analysis += "  [SELL] - Bearish signals dominate\n"
        elif score == 1:
            analysis += "  [WEAK BUY] - Slight bullish bias\n"
        elif score == -1:
            analysis += "  [WEAK SELL] - Slight bearish bias\n"
        else:
            analysis += "  [HOLD] - Neutral signals\n"
        
        analysis += f"\nTIP: Hover over charts for detailed data!\n"
        analysis += "=======================\n"
        
        self.update_text(analysis)

    def stop_progress(self):
        """Stop progress and re-enable button"""
        self.progress.stop()
        self.analyze_btn.config(state='normal', text="ANALYZE", 
                               bg=self.colors['button_bg'])
        self.results_text.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = StockAnalyzerGUI(root)
    root.mainloop()





