# 🚀 HyperFreq - Freqtrade for Hyperliquid (Machine Installation)

**✅ SUCCESSFULLY INSTALLED AND CONFIGURED ON THIS LINUX MINT MACHINE**

## 📋 Installation Summary

Your HyperFreq trading system is now **fully installed and operational** on this machine with:

- ✅ **Freqtrade 2025.6** properly installed with Python 3.11
- ✅ **Hyperliquid API credentials** configured and tested
- ✅ **MovingAverageCrossStrategy** with your exact specifications
- ✅ **Testnet & Mainnet** configurations ready
- ✅ **50 highest-volume pairs** auto-selection configured
- ✅ **1-minute timeframe** for maximum responsiveness

## 🎯 Your Trading Configuration

### Strategy Parameters (MovingAverageCrossStrategy)
- **Position Size**: $10.00 per trade
- **Stop Loss**: 10%
- **Take Profit**: 30%
- **Leverage**: 2x
- **Timeframe**: 1 minute
- **Pairs**: Top 50 by volume (auto-updated every 30 minutes)
- **Trading Mode**: Futures (perpetual contracts)
- **Margin Mode**: Isolated

### API Credentials (Configured)
- **Wallet Address**: `0x78b70c6265F089fd64af7C9b8Fc80e9f371D730A`
- **API Key**: `0xc617643210fd1af0591649f04560647776f2ba6a`
- **API Secret**: `0xa2df0be8f3ed00889d3769390cd31c9ea8560d27a4ed217e7ce272843958b394`

## 🔧 Quick Start Commands

### Management Script
```bash
# Interactive menu
./hyperfreq

# Check system status
./hyperfreq status

# Test API connection
./hyperfreq test

# Start trading on testnet (RECOMMENDED FIRST)
./hyperfreq testnet

# Start trading on mainnet (LIVE FUNDS)
./hyperfreq mainnet
```

### Direct Freqtrade Commands
```bash
# Test API connection
python test_hyperliquid_freqtrade.py

# Start testnet trading
freqtrade trade --config user_data/config_hyperliquid_testnet.json

# Start mainnet trading
freqtrade trade --config user_data/config_hyperliquid_mainnet.json

# Test pairlist selection
freqtrade test-pairlist --config user_data/config_hyperliquid_testnet.json

# Download historical data
freqtrade download-data --config user_data/config_hyperliquid_testnet.json --timerange 20241201-

# Run backtest
freqtrade backtesting --config user_data/config_hyperliquid_testnet.json --strategy MovingAverageCrossStrategy
```

## 📁 File Locations

```
/app/
├── hyperfreq                                    # Main management script
├── test_hyperliquid_freqtrade.py              # API connection test
└── user_data/                                  # Freqtrade user data
    ├── config_hyperliquid_testnet.json        # Testnet configuration
    ├── config_hyperliquid_mainnet.json        # Mainnet configuration
    ├── strategies/
    │   └── MovingAverageCrossStrategy.py       # Your trading strategy
    ├── logs/                                   # Trading logs
    ├── data/                                   # Market data cache
    └── backtest_results/                       # Backtest outputs
```

## 🚦 Getting Started (Step by Step)

### 1. **Verify Installation**
```bash
cd /app
./hyperfreq status
```
Should show all green checkmarks ✅

### 2. **Test API Connection**
```bash
./hyperfreq test
```
Should show successful connection to Hyperliquid testnet

### 3. **Start Safe Testing**
```bash
./hyperfreq testnet
```
This starts trading on Hyperliquid testnet (no real money risk)

### 4. **Monitor Trading**
- Watch the console output for trade signals
- Check `/app/user_data/logs/freqtrade.log` for detailed logs
- Press `Ctrl+C` to stop trading

### 5. **When Ready for Live Trading**
```bash
./hyperfreq mainnet
```
⚠️ **WARNING**: This trades with real money!

## 📊 Strategy Details

### Moving Average Crossover Logic
- **Entry Long**: Fast MA (10) crosses above Slow MA (20) + confirmations
- **Entry Short**: Fast MA crosses below Slow MA + confirmations
- **Exit**: Opposite crossover or RSI extremes or MACD reversal
- **Confirmations**: Volume, RSI, MACD, Bollinger Bands

### Risk Management
- **Hard Stop Loss**: 10% maximum loss per trade
- **Take Profit**: 30% target profit
- **Position Sizing**: Fixed $10 per trade
- **Maximum Open Trades**: 10 simultaneous positions
- **Leverage**: 2x (isolated margin)

## 🔄 Environment Switching

### Testnet (Safe Testing)
- **Purpose**: Test strategy without risk
- **Funds**: Simulated/test funds
- **Config**: `config_hyperliquid_testnet.json`
- **Database**: `tradesv3_testnet.sqlite`

### Mainnet (Live Trading)
- **Purpose**: Real trading with actual funds
- **Funds**: Your real USDC balance
- **Config**: `config_hyperliquid_mainnet.json`
- **Database**: `tradesv3_mainnet.sqlite`

## 📈 Monitoring & Analysis

### Log Files
```bash
# Real-time trading logs
tail -f user_data/logs/freqtrade.log

# Trading performance
freqtrade show_trades --config user_data/config_hyperliquid_testnet.json

# Profit summary
freqtrade profit --config user_data/config_hyperliquid_testnet.json
```

### Database Access
```bash
# SQLite database with all trade data
sqlite3 user_data/tradesv3_testnet.sqlite

# Query example: Show recent trades
sqlite3 user_data/tradesv3_testnet.sqlite "SELECT * FROM trades ORDER BY id DESC LIMIT 10;"
```

## 🔧 Advanced Configuration

### Modify Strategy Parameters
Edit `/app/user_data/strategies/MovingAverageCrossStrategy.py`:
- Change MA periods (fast_ma_period, slow_ma_period)
- Adjust risk parameters (stoploss, take_profit_percent)
- Add new indicators or conditions

### Modify Trading Settings
Edit config files to adjust:
- Position size (`stake_amount`)
- Maximum trades (`max_open_trades`)
- Leverage (`leverage`)
- Timeframe (`timeframe`)

## 🚨 Important Safety Notes

### Before Live Trading
1. **Test thoroughly on testnet first**
2. **Run backtests to validate strategy**
3. **Start with small position sizes**
4. **Monitor closely for first few trades**

### Risk Warnings
- **Never risk more than you can afford to lose**
- **Cryptocurrency trading involves significant risk**
- **Past performance doesn't guarantee future results**
- **Keep API credentials secure**

## 🔍 Troubleshooting

### Common Issues

**"No pairs found"**
```bash
# Check exchange connection
./hyperfreq test

# Test pairlist configuration
./hyperfreq pairlist
```

**"Insufficient balance"**
- Check your USDC balance on Hyperliquid
- Reduce position size in config if needed
- Ensure you have enough for 10 concurrent trades

**Strategy not generating signals**
- Check market conditions (trending vs. sideways)
- Review strategy parameters
- Monitor logs for debugging info

### Getting Help
```bash
# Show detailed help
freqtrade --help

# Strategy-specific help
freqtrade backtesting --help

# Check configuration
freqtrade show-config --config user_data/config_hyperliquid_testnet.json
```

## 🎉 Success! You're Ready to Trade

Your HyperFreq system is **fully operational** and ready for Hyperliquid trading!

### Next Steps:
1. **Start with testnet**: `./hyperfreq testnet`
2. **Monitor performance** for a few days
3. **Adjust parameters** if needed
4. **Move to mainnet** when confident

---

**Installation completed successfully! 🚀**

*For any issues, check the logs in `/app/user_data/logs/` or run `./hyperfreq status` to verify configuration.*