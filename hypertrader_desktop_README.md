# Hypertrader 1.5 - Standalone Windows Desktop Application

A comprehensive cryptocurrency trading application for Windows with real-time Hyperliquid integration.

## Structure

```
hypertrader/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── config/
│   ├── __init__.py
│   ├── settings.py         # Application settings and configuration
│   └── api_config.py       # API configuration management
├── core/
│   ├── __init__.py
│   ├── hyperliquid_client.py  # Hyperliquid API integration
│   ├── data_manager.py     # Data management and storage
│   └── trading_engine.py   # Trading logic and order management
├── ui/
│   ├── __init__.py
│   ├── main_window.py      # Main application window
│   ├── components/
│   │   ├── __init__.py
│   │   ├── dashboard.py    # Portfolio dashboard
│   │   ├── trading_panel.py # Trading interface
│   │   ├── markets_view.py # Market data viewer
│   │   ├── portfolio_view.py # Portfolio management
│   │   ├── strategies_view.py # Strategy management
│   │   └── settings_view.py # Settings and configuration
│   └── styles/
│       ├── __init__.py
│       └── themes.py       # UI themes and styling
├── models/
│   ├── __init__.py
│   ├── account.py          # Account data models
│   ├── position.py         # Position models
│   ├── order.py           # Order models
│   └── strategy.py        # Strategy models
├── utils/
│   ├── __init__.py
│   ├── helpers.py         # Utility functions
│   ├── logger.py          # Logging configuration
│   └── validators.py      # Data validation
├── data/
│   ├── database.db        # Local SQLite database
│   └── logs/              # Application logs
└── assets/
    ├── icons/             # Application icons
    ├── images/            # UI images and graphics
    └── sounds/            # Notification sounds
```

## Features

- Real-time Hyperliquid API integration
- Portfolio management and tracking
- Advanced trading interface with order management
- Market data visualization
- Strategy creation and backtesting
- Risk management tools
- Local data storage with SQLite
- Modern desktop UI with themes
- Audio notifications
- Export/import capabilities

## Installation

1. Install Python 3.8+
2. Install requirements: `pip install -r requirements.txt`
3. Run application: `python main.py`

## Configuration

Set your Hyperliquid API credentials in the Settings panel or edit `config/api_config.py`.