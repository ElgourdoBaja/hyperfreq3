#!/usr/bin/env python3
"""
Hypertrader 1.5 - Standalone Windows Desktop Application
Main application entry point
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import logging
from pathlib import Path

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import application components
from config.settings import AppSettings
from utils.logger import setup_logging
from ui.main_window import MainWindow

class HypertraderApp:
    """Main application class"""
    
    def __init__(self):
        self.settings = AppSettings()
        self.setup_logging()
        self.root = None
        self.main_window = None
        
    def setup_logging(self):
        """Setup application logging"""
        try:
            setup_logging(self.settings.get('logging_level', 'INFO'))
            self.logger = logging.getLogger(__name__)
            self.logger.info("Hypertrader 1.5 starting...")
        except Exception as e:
            print(f"Failed to setup logging: {e}")
            
    def check_requirements(self):
        """Check if all requirements are met"""
        try:
            import requests
            import sqlite3
            import json
            from datetime import datetime
            return True
        except ImportError as e:
            messagebox.showerror(
                "Missing Dependencies", 
                f"Required package not found: {e}\n\nPlease install requirements:\npip install -r requirements.txt"
            )
            return False
            
    def create_directories(self):
        """Create necessary directories"""
        directories = [
            PROJECT_ROOT / "data",
            PROJECT_ROOT / "data" / "logs",
            PROJECT_ROOT / "assets",
            PROJECT_ROOT / "assets" / "icons",
            PROJECT_ROOT / "assets" / "images",
            PROJECT_ROOT / "assets" / "sounds"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
    def run(self):
        """Run the application"""
        try:
            # Check requirements
            if not self.check_requirements():
                return
                
            # Create necessary directories
            self.create_directories()
            
            # Create the main window
            self.root = tk.Tk()
            self.root.title("Hypertrader 1.5 - Cryptocurrency Trading Platform")
            self.root.geometry("1200x800")
            self.root.minsize(1000, 600)
            
            # Set icon (if available)
            try:
                icon_path = PROJECT_ROOT / "assets" / "icons" / "hypertrader.ico"
                if icon_path.exists():
                    self.root.iconbitmap(str(icon_path))
            except Exception as e:
                self.logger.warning(f"Could not load application icon: {e}")
            
            # Create main window
            self.main_window = MainWindow(self.root, self.settings)
            
            # Setup window close handler
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Start the application
            self.logger.info("Hypertrader 1.5 started successfully")
            self.root.mainloop()
            
        except Exception as e:
            error_msg = f"Failed to start Hypertrader: {e}"
            self.logger.error(error_msg, exc_info=True)
            messagebox.showerror("Startup Error", error_msg)
            
    def on_closing(self):
        """Handle application closing"""
        try:
            if messagebox.askokcancel("Quit", "Do you want to quit Hypertrader?"):
                self.logger.info("Hypertrader 1.5 shutting down...")
                
                # Save settings
                self.settings.save()
                
                # Close main window
                if self.main_window:
                    self.main_window.cleanup()
                    
                # Destroy root window
                if self.root:
                    self.root.destroy()
                    
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            if self.root:
                self.root.destroy()

def main():
    """Main function"""
    try:
        app = HypertraderApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()