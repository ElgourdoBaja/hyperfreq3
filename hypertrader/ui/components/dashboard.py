"""
Dashboard component for portfolio overview
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional

from config.settings import AppSettings
from core.hyperliquid_client import HyperliquidClient
from utils.helpers import format_currency, format_percentage

class DashboardFrame(ttk.Frame):
    """Dashboard frame showing portfolio overview"""
    
    def __init__(self, parent, settings: AppSettings, hyperliquid_client: Optional[HyperliquidClient]):
        super().__init__(parent)
        self.settings = settings
        self.hyperliquid_client = hyperliquid_client
        self.logger = logging.getLogger(__name__)
        
        # Data
        self.account_data = None
        self.portfolio_data = None
        
        # UI components
        self.account_frame = None
        self.positions_frame = None
        
        self._setup_ui()
        self.refresh_data()
        
    def _setup_ui(self):
        """Setup dashboard UI"""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Portfolio Dashboard", font=("Arial", 16, "bold"))
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Account overview section
        self._create_account_section(main_frame)
        
        # Positions section
        self._create_positions_section(main_frame)
        
    def _create_account_section(self, parent):
        """Create account overview section"""
        # Account frame
        self.account_frame = ttk.LabelFrame(parent, text="Account Overview", padding=10)
        self.account_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Account metrics grid
        metrics_frame = ttk.Frame(self.account_frame)
        metrics_frame.pack(fill=tk.X)
        
        # Configure grid
        for i in range(4):
            metrics_frame.grid_columnconfigure(i, weight=1)
            
        # Account value
        self.account_value_label = ttk.Label(metrics_frame, text="Account Value")
        self.account_value_label.grid(row=0, column=0, sticky=tk.W, padx=5)
        self.account_value_var = tk.StringVar(value="$0.00")
        self.account_value_display = ttk.Label(metrics_frame, textvariable=self.account_value_var, font=("Arial", 14, "bold"))
        self.account_value_display.grid(row=1, column=0, sticky=tk.W, padx=5)
        
        # Available balance
        self.available_label = ttk.Label(metrics_frame, text="Available Balance")
        self.available_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        self.available_var = tk.StringVar(value="$0.00")
        self.available_display = ttk.Label(metrics_frame, textvariable=self.available_var, font=("Arial", 14, "bold"))
        self.available_display.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Margin used
        self.margin_label = ttk.Label(metrics_frame, text="Margin Used")
        self.margin_label.grid(row=0, column=2, sticky=tk.W, padx=5)
        self.margin_var = tk.StringVar(value="$0.00")
        self.margin_display = ttk.Label(metrics_frame, textvariable=self.margin_var, font=("Arial", 14, "bold"))
        self.margin_display.grid(row=1, column=2, sticky=tk.W, padx=5)
        
        # Total PnL
        self.pnl_label = ttk.Label(metrics_frame, text="Total PnL")
        self.pnl_label.grid(row=0, column=3, sticky=tk.W, padx=5)
        self.pnl_var = tk.StringVar(value="$0.00")
        self.pnl_display = ttk.Label(metrics_frame, textvariable=self.pnl_var, font=("Arial", 14, "bold"))
        self.pnl_display.grid(row=1, column=3, sticky=tk.W, padx=5)
        
    def _create_positions_section(self, parent):
        """Create positions section"""
        # Positions frame
        self.positions_frame = ttk.LabelFrame(parent, text="Open Positions", padding=10)
        self.positions_frame.pack(fill=tk.BOTH, expand=True)
        
        # Positions treeview
        columns = ("coin", "side", "size", "entry_price", "current_price", "pnl")
        self.positions_tree = ttk.Treeview(self.positions_frame, columns=columns, show="headings", height=8)
        
        # Configure columns
        self.positions_tree.heading("coin", text="Asset")
        self.positions_tree.heading("side", text="Side")
        self.positions_tree.heading("size", text="Size")
        self.positions_tree.heading("entry_price", text="Entry Price")
        self.positions_tree.heading("current_price", text="Current Price")
        self.positions_tree.heading("pnl", text="PnL")
        
        # Column widths
        self.positions_tree.column("coin", width=80)
        self.positions_tree.column("side", width=60)
        self.positions_tree.column("size", width=100)
        self.positions_tree.column("entry_price", width=100)
        self.positions_tree.column("current_price", width=100)
        self.positions_tree.column("pnl", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.positions_frame, orient=tk.VERTICAL, command=self.positions_tree.yview)
        self.positions_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.positions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # No positions message
        self.no_positions_label = ttk.Label(self.positions_frame, text="No open positions", foreground="gray")
        
    def refresh_data(self):
        """Refresh dashboard data"""
        try:
            if not self.hyperliquid_client:
                self._update_no_connection()
                return
                
            # Get account info
            self.account_data = self.hyperliquid_client.get_account_info()
            
            # Get portfolio
            self.portfolio_data = self.hyperliquid_client.get_portfolio()
            
            # Update UI
            self._update_account_display()
            self._update_positions_display()
            
            self.logger.info("Dashboard data refreshed")
            
        except Exception as e:
            self.logger.error(f"Error refreshing dashboard data: {e}")
            self._update_error_display(str(e))
            
    def _update_account_display(self):
        """Update account metrics display"""
        if self.account_data:
            self.account_value_var.set(format_currency(self.account_data.account_value))
            self.available_var.set(format_currency(self.account_data.available_balance))
            self.margin_var.set(format_currency(self.account_data.margin_used))
            
            # Color code PnL
            pnl_text = format_currency(self.account_data.total_pnl)
            self.pnl_var.set(pnl_text)
            
            if self.account_data.total_pnl >= 0:
                self.pnl_display.configure(foreground="green")
            else:
                self.pnl_display.configure(foreground="red")
        else:
            self._update_no_connection()
            
    def _update_positions_display(self):
        """Update positions display"""
        # Clear existing items
        for item in self.positions_tree.get_children():
            self.positions_tree.delete(item)
            
        if self.portfolio_data and self.portfolio_data.positions:
            # Hide no positions message
            self.no_positions_label.pack_forget()
            
            # Add positions to tree
            for position in self.portfolio_data.positions:
                # Format values
                side_text = position.side.value if position.side else "Unknown"
                size_text = f"{position.size:.4f}"
                entry_price_text = format_currency(position.entry_price)
                current_price_text = format_currency(position.current_price)
                pnl_text = format_currency(position.unrealized_pnl)
                
                # Insert row
                item = self.positions_tree.insert("", tk.END, values=(
                    position.coin,
                    side_text,
                    size_text,
                    entry_price_text,
                    current_price_text,
                    pnl_text
                ))
                
                # Color code PnL
                if position.unrealized_pnl >= 0:
                    self.positions_tree.set(item, "pnl", f"+{pnl_text}")
                    # Note: Treeview doesn't easily support individual cell colors
                else:
                    self.positions_tree.set(item, "pnl", pnl_text)
        else:
            # Show no positions message
            if hasattr(self, 'no_positions_label'):
                self.no_positions_label.pack(expand=True)
                
    def _update_no_connection(self):
        """Update display for no connection"""
        self.account_value_var.set("No Connection")
        self.available_var.set("$0.00")
        self.margin_var.set("$0.00")
        self.pnl_var.set("$0.00")
        self.pnl_display.configure(foreground="black")
        
        # Clear positions
        for item in self.positions_tree.get_children():
            self.positions_tree.delete(item)
            
    def _update_error_display(self, error_msg: str):
        """Update display for error state"""
        self.account_value_var.set("Error")
        self.available_var.set("Error")
        self.margin_var.set("Error")
        self.pnl_var.set("Error")
        self.pnl_display.configure(foreground="red")
        
        self.logger.error(f"Dashboard error: {error_msg}")
        
    def cleanup(self):
        """Cleanup resources"""
        # Nothing special to cleanup for dashboard
        pass