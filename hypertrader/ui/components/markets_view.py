"""
Markets view component
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional

from config.settings import AppSettings
from core.hyperliquid_client import HyperliquidClient

class MarketsFrame(ttk.Frame):
    """Markets frame for market data viewing"""
    
    def __init__(self, parent, settings: AppSettings, hyperliquid_client: Optional[HyperliquidClient]):
        super().__init__(parent)
        self.settings = settings
        self.hyperliquid_client = hyperliquid_client
        self.logger = logging.getLogger(__name__)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup markets UI"""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Market Data", font=("Arial", 16, "bold"))
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Placeholder content
        content_label = ttk.Label(main_frame, text="Market data and charts will be implemented here.", foreground="gray")
        content_label.pack(expand=True)
        
    def refresh_data(self):
        """Refresh market data"""
        pass
        
    def cleanup(self):
        """Cleanup resources"""
        pass