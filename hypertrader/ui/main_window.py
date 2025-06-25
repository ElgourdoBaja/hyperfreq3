"""
Main application window
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, Any

from config.settings import AppSettings
from config.api_config import APIConfigManager
from core.hyperliquid_client import HyperliquidClient
from ui.components.dashboard import DashboardFrame
from ui.components.trading_panel import TradingFrame
from ui.components.portfolio_view import PortfolioFrame
from ui.components.strategies_view import StrategiesFrame
from ui.components.markets_view import MarketsFrame
from ui.components.settings_view import SettingsFrame

class MainWindow:
    """Main application window"""
    
    def __init__(self, root: tk.Tk, settings: AppSettings):
        self.root = root
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
        # Initialize API manager and client
        self.api_manager = APIConfigManager()
        self.api_manager.load_from_settings(settings._settings)
        
        self.hyperliquid_client = None
        self._init_api_client()
        
        # UI components
        self.notebook = None
        self.frames = {}
        
        # Data refresh timer
        self.refresh_timer = None
        
        # Initialize UI
        self._setup_ui()
        self._setup_menu()
        self._start_refresh_timer()
        
    def _init_api_client(self):
        """Initialize Hyperliquid API client"""
        try:
            if self.api_manager.hyperliquid.is_configured():
                self.hyperliquid_client = HyperliquidClient(self.api_manager.hyperliquid)
                self.logger.info("Hyperliquid client initialized")
            else:
                self.logger.info("Hyperliquid client not initialized - missing credentials")
        except Exception as e:
            self.logger.error(f"Failed to initialize API client: {e}")
            
    def _setup_ui(self):
        """Setup main UI components"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors for dark theme
        style.configure('TNotebook', background='#2b2b2b')
        style.configure('TNotebook.Tab', background='#404040', foreground='white')
        style.map('TNotebook.Tab', background=[('selected', '#0078d4')])
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self._create_tabs()
        
        # Status bar
        self._create_status_bar(main_frame)
        
    def _create_tabs(self):
        """Create all application tabs"""
        tabs = [
            ("Dashboard", DashboardFrame),
            ("Trading", TradingFrame),
            ("Portfolio", PortfolioFrame),
            ("Markets", MarketsFrame),
            ("Strategies", StrategiesFrame),
            ("Settings", SettingsFrame)
        ]
        
        for tab_name, frame_class in tabs:
            try:
                # Create frame
                frame = frame_class(
                    self.notebook, 
                    self.settings, 
                    self.hyperliquid_client
                )
                
                # Add to notebook
                self.notebook.add(frame, text=tab_name)
                
                # Store reference
                self.frames[tab_name.lower()] = frame
                
                self.logger.info(f"Created {tab_name} tab")
                
            except Exception as e:
                self.logger.error(f"Failed to create {tab_name} tab: {e}")
                
                # Create error frame
                error_frame = ttk.Frame(self.notebook)
                error_label = ttk.Label(
                    error_frame, 
                    text=f"Error loading {tab_name}: {e}",
                    foreground="red"
                )
                error_label.pack(expand=True)
                self.notebook.add(error_frame, text=tab_name)
                
    def _create_status_bar(self, parent):
        """Create status bar"""
        self.status_frame = ttk.Frame(parent)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Connection status
        self.connection_status = ttk.Label(
            self.status_frame, 
            text="Disconnected",
            foreground="red"
        )
        self.connection_status.pack(side=tk.LEFT, padx=5)
        
        # Account balance
        self.balance_label = ttk.Label(
            self.status_frame,
            text="Balance: $0.00"
        )
        self.balance_label.pack(side=tk.LEFT, padx=20)
        
        # Last update time
        self.update_time_label = ttk.Label(
            self.status_frame,
            text="Last update: Never"
        )
        self.update_time_label.pack(side=tk.RIGHT, padx=5)
        
    def _setup_menu(self):
        """Setup application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import Settings...", command=self._import_settings)
        file_menu.add_command(label="Export Settings...", command=self._export_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Test API Connection", command=self._test_api_connection)
        tools_menu.add_command(label="Refresh Data", command=self._refresh_all_data)
        tools_menu.add_separator()
        tools_menu.add_command(label="Clear Cache", command=self._clear_cache)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Dashboard", command=lambda: self._switch_tab(0))
        view_menu.add_command(label="Trading", command=lambda: self._switch_tab(1))
        view_menu.add_command(label="Portfolio", command=lambda: self._switch_tab(2))
        view_menu.add_command(label="Markets", command=lambda: self._switch_tab(3))
        view_menu.add_command(label="Strategies", command=lambda: self._switch_tab(4))
        view_menu.add_command(label="Settings", command=lambda: self._switch_tab(5))
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        
    def _switch_tab(self, index: int):
        """Switch to specific tab"""
        try:
            self.notebook.select(index)
        except tk.TclError:
            pass
            
    def _start_refresh_timer(self):
        """Start data refresh timer"""
        refresh_interval = self.settings.get('ui.refresh_interval', 5000)
        self.refresh_timer = self.root.after(refresh_interval, self._periodic_refresh)
        
    def _periodic_refresh(self):
        """Periodic data refresh"""
        try:
            # Update status bar
            self._update_status_bar()
            
            # Refresh current tab
            current_tab = self.notebook.index(self.notebook.select())
            tab_names = ["dashboard", "trading", "portfolio", "markets", "strategies", "settings"]
            
            if current_tab < len(tab_names):
                current_frame = self.frames.get(tab_names[current_tab])
                if current_frame and hasattr(current_frame, 'refresh_data'):
                    current_frame.refresh_data()
                    
        except Exception as e:
            self.logger.error(f"Error in periodic refresh: {e}")
            
        # Schedule next refresh
        refresh_interval = self.settings.get('ui.refresh_interval', 5000)
        self.refresh_timer = self.root.after(refresh_interval, self._periodic_refresh)
        
    def _update_status_bar(self):
        """Update status bar information"""
        try:
            # Update connection status
            if self.hyperliquid_client and self.hyperliquid_client.test_connection():
                self.connection_status.config(text="Connected", foreground="green")
                
                # Update balance
                account = self.hyperliquid_client.get_account_info()
                if account:
                    balance_text = f"Balance: ${account.account_value:.2f}"
                    self.balance_label.config(text=balance_text)
            else:
                self.connection_status.config(text="Disconnected", foreground="red")
                self.balance_label.config(text="Balance: $0.00")
                
            # Update timestamp
            from datetime import datetime
            self.update_time_label.config(
                text=f"Last update: {datetime.now().strftime('%H:%M:%S')}"
            )
            
        except Exception as e:
            self.logger.error(f"Error updating status bar: {e}")
            
    def _test_api_connection(self):
        """Test API connection"""
        try:
            if not self.hyperliquid_client:
                messagebox.showerror("Error", "API client not initialized. Please configure credentials in Settings.")
                return
                
            if self.hyperliquid_client.test_connection():
                messagebox.showinfo("Success", "API connection successful!")
            else:
                messagebox.showerror("Error", "API connection failed. Please check your credentials.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Connection test failed: {e}")
            
    def _refresh_all_data(self):
        """Refresh all data"""
        try:
            for frame in self.frames.values():
                if hasattr(frame, 'refresh_data'):
                    frame.refresh_data()
            messagebox.showinfo("Success", "Data refreshed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh data: {e}")
            
    def _clear_cache(self):
        """Clear application cache"""
        try:
            if self.hyperliquid_client:
                self.hyperliquid_client.last_update.clear()
            messagebox.showinfo("Success", "Cache cleared successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear cache: {e}")
            
    def _import_settings(self):
        """Import settings from file"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Import Settings",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.settings.import_settings(file_path)
                messagebox.showinfo("Success", "Settings imported successfully!")
                # Reinitialize API client
                self._init_api_client()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import settings: {e}")
                
    def _export_settings(self):
        """Export settings to file"""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            title="Export Settings",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.settings.export_settings(file_path)
                messagebox.showinfo("Success", "Settings exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export settings: {e}")
                
    def _show_about(self):
        """Show about dialog"""
        about_text = """
Hypertrader 1.5
Cryptocurrency Trading Platform

A comprehensive desktop application for cryptocurrency trading
with real-time Hyperliquid integration.

Features:
• Real-time market data
• Portfolio management
• Strategy development
• Risk management tools
• Professional trading interface

Version: 1.5.0
"""
        messagebox.showinfo("About Hypertrader 1.5", about_text)
        
    def update_api_credentials(self, wallet_address: str, api_key: str, api_secret: str, environment: str):
        """Update API credentials and reinitialize client"""
        try:
            # Update settings
            self.settings.set_api_credentials(wallet_address, api_key, api_secret, environment)
            
            # Update API manager
            self.api_manager.load_from_settings(self.settings._settings)
            
            # Reinitialize client
            self._init_api_client()
            
            self.logger.info("API credentials updated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update API credentials: {e}")
            return False
            
    def get_hyperliquid_client(self):
        """Get the Hyperliquid client"""
        return self.hyperliquid_client
        
    def cleanup(self):
        """Cleanup resources"""
        try:
            # Cancel refresh timer
            if self.refresh_timer:
                self.root.after_cancel(self.refresh_timer)
                
            # Cleanup API client
            if self.hyperliquid_client:
                self.hyperliquid_client.cleanup()
                
            # Cleanup frames
            for frame in self.frames.values():
                if hasattr(frame, 'cleanup'):
                    frame.cleanup()
                    
            self.logger.info("Main window cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")