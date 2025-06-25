"""
Settings view component
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Optional

from config.settings import AppSettings
from core.hyperliquid_client import HyperliquidClient
from utils.helpers import validate_wallet_address, validate_private_key

class SettingsFrame(ttk.Frame):
    """Settings frame for configuration"""
    
    def __init__(self, parent, settings: AppSettings, hyperliquid_client: Optional[HyperliquidClient]):
        super().__init__(parent)
        self.settings = settings
        self.hyperliquid_client = hyperliquid_client
        self.logger = logging.getLogger(__name__)
        
        # Variables
        self.wallet_address_var = tk.StringVar()
        self.api_key_var = tk.StringVar()
        self.api_secret_var = tk.StringVar()
        self.environment_var = tk.StringVar()
        
        self._setup_ui()
        self._load_current_settings()
        
    def _setup_ui(self):
        """Setup settings UI"""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Settings", font=("Arial", 16, "bold"))
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Create sections
        self._create_api_section(main_frame)
        self._create_ui_section(main_frame)
        self._create_trading_section(main_frame)
        
        # Buttons
        self._create_buttons_section(main_frame)
        
    def _create_api_section(self, parent):
        """Create API credentials section"""
        api_frame = ttk.LabelFrame(parent, text="Hyperliquid API Configuration", padding=10)
        api_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Wallet address
        ttk.Label(api_frame, text="Wallet Address:").grid(row=0, column=0, sticky=tk.W, pady=2)
        wallet_entry = ttk.Entry(api_frame, textvariable=self.wallet_address_var, width=50)
        wallet_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=2, padx=(10, 0))
        
        # API Key
        ttk.Label(api_frame, text="API Key:").grid(row=1, column=0, sticky=tk.W, pady=2)
        api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, width=50)
        api_key_entry.grid(row=1, column=1, sticky=tk.W+tk.E, pady=2, padx=(10, 0))
        
        # API Secret
        ttk.Label(api_frame, text="API Secret:").grid(row=2, column=0, sticky=tk.W, pady=2)
        api_secret_entry = ttk.Entry(api_frame, textvariable=self.api_secret_var, width=50, show="*")
        api_secret_entry.grid(row=2, column=1, sticky=tk.W+tk.E, pady=2, padx=(10, 0))
        
        # Environment
        ttk.Label(api_frame, text="Environment:").grid(row=3, column=0, sticky=tk.W, pady=2)
        env_combo = ttk.Combobox(api_frame, textvariable=self.environment_var, values=["mainnet", "testnet"], state="readonly")
        env_combo.grid(row=3, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        # Configure grid weights
        api_frame.grid_columnconfigure(1, weight=1)
        
        # Test connection button
        test_button = ttk.Button(api_frame, text="Test Connection", command=self._test_connection)
        test_button.grid(row=4, column=1, sticky=tk.W, pady=(10, 0), padx=(10, 0))
        
    def _create_ui_section(self, parent):
        """Create UI settings section"""
        ui_frame = ttk.LabelFrame(parent, text="UI Settings", padding=10)
        ui_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Theme (placeholder)
        ttk.Label(ui_frame, text="Theme:").grid(row=0, column=0, sticky=tk.W, pady=2)
        theme_combo = ttk.Combobox(ui_frame, values=["Dark", "Light"], state="readonly")
        theme_combo.set("Dark")
        theme_combo.grid(row=0, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        # Refresh interval
        ttk.Label(ui_frame, text="Refresh Interval (ms):").grid(row=1, column=0, sticky=tk.W, pady=2)
        refresh_var = tk.StringVar(value=str(self.settings.get('ui.refresh_interval', 5000)))
        refresh_entry = ttk.Entry(ui_frame, textvariable=refresh_var, width=10)
        refresh_entry.grid(row=1, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
    def _create_trading_section(self, parent):
        """Create trading settings section"""
        trading_frame = ttk.LabelFrame(parent, text="Trading Settings", padding=10)
        trading_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Default order size
        ttk.Label(trading_frame, text="Default Order Size:").grid(row=0, column=0, sticky=tk.W, pady=2)
        order_size_var = tk.StringVar(value=str(self.settings.get('trading.default_order_size', 0.1)))
        order_size_entry = ttk.Entry(trading_frame, textvariable=order_size_var, width=10)
        order_size_entry.grid(row=0, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        # Risk limit
        ttk.Label(trading_frame, text="Risk Limit (%):").grid(row=1, column=0, sticky=tk.W, pady=2)
        risk_var = tk.StringVar(value=str(self.settings.get('trading.risk_limit_percent', 2.0)))
        risk_entry = ttk.Entry(trading_frame, textvariable=risk_var, width=10)
        risk_entry.grid(row=1, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        # Confirm orders
        confirm_var = tk.BooleanVar(value=self.settings.get('trading.confirm_orders', True))
        confirm_check = ttk.Checkbutton(trading_frame, text="Confirm orders before placement", variable=confirm_var)
        confirm_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        
    def _create_buttons_section(self, parent):
        """Create buttons section"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Save button
        save_button = ttk.Button(buttons_frame, text="Save Settings", command=self._save_settings)
        save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Reset button
        reset_button = ttk.Button(buttons_frame, text="Reset to Defaults", command=self._reset_settings)
        reset_button.pack(side=tk.LEFT)
        
    def _load_current_settings(self):
        """Load current settings into the form"""
        creds = self.settings.get_api_credentials()
        self.wallet_address_var.set(creds.get("wallet_address", ""))
        self.api_key_var.set(creds.get("api_key", ""))
        self.api_secret_var.set(creds.get("api_secret", ""))
        self.environment_var.set(creds.get("environment", "mainnet"))
        
    def _save_settings(self):
        """Save settings"""
        try:
            # Validate inputs
            wallet_address = self.wallet_address_var.get().strip()
            api_key = self.api_key_var.get().strip()
            api_secret = self.api_secret_var.get().strip()
            environment = self.environment_var.get()
            
            if wallet_address and not validate_wallet_address(wallet_address):
                messagebox.showerror("Error", "Invalid wallet address format")
                return
                
            if api_secret and not validate_private_key(api_secret):
                messagebox.showerror("Error", "Invalid private key format")
                return
                
            # Save API credentials
            self.settings.set_api_credentials(wallet_address, api_key, api_secret, environment)
            
            # Update main window (if accessible)
            parent_widget = self.winfo_toplevel()
            if hasattr(parent_widget, 'main_window'):
                main_window = parent_widget.main_window
                if hasattr(main_window, 'update_api_credentials'):
                    main_window.update_api_credentials(wallet_address, api_key, api_secret, environment)
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            self.logger.info("Settings saved")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            self.logger.error(f"Error saving settings: {e}")
            
    def _reset_settings(self):
        """Reset settings to defaults"""
        if messagebox.askyesno("Confirm", "Are you sure you want to reset all settings to defaults?"):
            try:
                self.settings.reset_to_defaults()
                self._load_current_settings()
                messagebox.showinfo("Success", "Settings reset to defaults!")
                self.logger.info("Settings reset to defaults")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset settings: {e}")
                self.logger.error(f"Error resetting settings: {e}")
                
    def _test_connection(self):
        """Test API connection"""
        try:
            # Save current settings first
            self._save_settings()
            
            # Test connection
            if self.hyperliquid_client and self.hyperliquid_client.test_connection():
                messagebox.showinfo("Success", "API connection successful!")
            else:
                messagebox.showerror("Error", "API connection failed. Please check your credentials.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Connection test failed: {e}")
            
    def refresh_data(self):
        """Refresh settings data (reload from file)"""
        self._load_current_settings()
        
    def cleanup(self):
        """Cleanup resources"""
        pass