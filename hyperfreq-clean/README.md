# HyperFreq - Freqtrade for Hyperliquid

A fully configured Freqtrade setup for trading on Hyperliquid perpetual exchange with a simple moving average crossover strategy.

## 🚀 Features

- **Native Hyperliquid Support**: Uses Freqtrade 2024.11 with built-in Hyperliquid exchange integration
- **Testnet/Mainnet Switching**: Easy configuration switching between Hyperliquid testnet and mainnet
- **50 Top Volume Pairs**: Automatically trades the 50 highest-volume pairs on Hyperliquid
- **Moving Average Strategy**: Simple but effective moving average crossover strategy
- **Risk Management**: Built-in stop loss (10%) and take profit (30%) with 2x leverage
- **1-minute Timeframe**: Optimized for the shortest feasible timeframe on Hyperliquid
- **Easy Configuration**: Interactive setup script for API credentials

## 📋 Requirements

- Python 3.11 (as specified)
- Hyperliquid API credentials:
  - Main wallet address (MetaMask address)
  - API key (public identifier)
  - API secret key (private secret)

## 🔧 Getting Hyperliquid API Credentials

1. Visit [Hyperliquid API Management](https://app.hyperliquid.xyz/API)
2. Copy your **main wallet address** from the top-right dropdown
3. Enter a descriptive name for your API wallet
4. Click "Generate" to create the API wallet
5. Copy the **API Key** (public identifier)
6. Click "Authorize API Wallet" to reveal the **API Secret Key**
7. Copy the **API Secret Key** (private secret)
8. Store all three values securely

## ⚡ Quick Start

### 1. Configure API Credentials

Run the interactive configuration script:

```bash
./configure.sh
```

Or use the direct command:

```bash
./configure.sh configure
```

This will prompt you for:
- Hyperliquid main wallet address
- API key
- API secret key
- Environment choice (testnet/mainnet/both)

### 2. Start Trading

For testnet (recommended first):
```bash
./configure.sh run-testnet
```

For mainnet (live trading):
```bash
./configure.sh run-mainnet
```

### 3. Optional: Download Historical Data & Backtest

Download data for backtesting:
```bash
./configure.sh download-testnet
```

Run a backtest:
```bash
./configure.sh backtest-testnet
```

## 📁 Project Structure

```
/app/freqtrade/
├── configure.sh                           # Main configuration script
├── user_data/
│   ├── config_hyperliquid_testnet.json   # Testnet configuration
│   ├── config_hyperliquid_mainnet.json   # Mainnet configuration
│   └── strategies/
│       └── MovingAverageCrossStrategy.py  # Trading strategy
├── freqtrade/
│   └── exchange/
│       └── hyperliquid.py                 # Native Hyperliquid support
└── README_HYPERFREQ.md                   # This file
```

## 🎯 Strategy Details

### MovingAverageCrossStrategy

- **Type**: Moving Average Crossover
- **Timeframe**: 1 minute (shortest feasible for Hyperliquid)
- **Entry Signals**:
  - **Long**: Fast MA crosses above Slow MA + volume confirmation + RSI < 70 + MACD bullish + price above BB middle
  - **Short**: Fast MA crosses below Slow MA + volume confirmation + RSI > 30 + MACD bearish + price below BB middle
- **Exit Signals**:
  - **Long**: Fast MA crosses below Slow MA OR RSI > 80 OR MACD turns bearish
  - **Short**: Fast MA crosses above Slow MA OR RSI < 20 OR MACD turns bullish
- **Risk Management**:
  - Stop Loss: 10%
  - Take Profit: 30%
  - Leverage: 2x
  - Position Size: $10.00 per trade

### Strategy Parameters

- **Fast MA Period**: 10 (optimizable: 5-20)
- **Slow MA Period**: 20 (optimizable: 20-50)
- **RSI Period**: 14
- **Volume SMA**: 20
- **Bollinger Bands**: 20 periods

## ⚙️ Configuration Details

### Key Settings

- **Max Open Trades**: 10
- **Stake Currency**: USDC
- **Stake Amount**: $10.00
- **Trading Mode**: Futures (perpetual)
- **Margin Mode**: Isolated
- **Leverage**: 2x
- **Pair Selection**: Top 50 by volume (auto-refreshed every 30 minutes)

### Pair List Configuration

The bot automatically selects the 50 highest-volume pairs using:
- `VolumePairList`: Sorts by quote volume
- `AgeFilter`: Minimum 1 day listed
- `PrecisionFilter`: Ensures proper precision
- `PriceFilter`: Filters out very low-price coins
- `SpreadFilter`: Maximum 0.5% spread

## 🔒 Security & Risk Management

### Built-in Protections

- **Stop Loss**: Hard 10% stop loss on all trades
- **Take Profit**: Automatic 30% take profit
- **Position Sizing**: Fixed $10 per trade to manage risk
- **Leverage Limit**: Capped at 2x leverage
- **Isolated Margin**: Each position isolated to prevent cascade liquidation

### Best Practices

1. **Start with Testnet**: Always test your strategy first
2. **Monitor Performance**: Check logs and performance regularly
3. **Risk Management**: Never risk more than you can afford to lose
4. **API Security**: Keep your API credentials secure and never share them
5. **Regular Updates**: Keep Freqtrade updated for latest features and security

## 📊 Monitoring & Management

### Available Commands

```bash
# Configuration
./configure.sh configure           # Set up API credentials
./configure.sh status              # Show configuration status

# Trading
./configure.sh run-testnet         # Start testnet trading
./configure.sh run-mainnet         # Start mainnet trading

# Data & Analysis
./configure.sh download-testnet    # Download historical data
./configure.sh backtest-testnet    # Run backtests
```

### Log Files

- **Trading Logs**: `user_data/logs/freqtrade.log`
- **Database**: `user_data/tradesv3.sqlite`
- **Backtest Results**: `user_data/backtest_results/`

## 🔄 Environment Switching

### Testnet to Mainnet

1. Ensure testnet configuration is working
2. Run backtests to validate strategy
3. Configure mainnet credentials: `./configure.sh configure`
4. Start mainnet trading: `./configure.sh run-mainnet`

### Configuration Files

- **Testnet**: `user_data/config_hyperliquid_testnet.json`
- **Mainnet**: `user_data/config_hyperliquid_mainnet.json`

The only differences between configurations:
- `sandbox: true/false` in ccxt_config
- Database files are separate

## 🚨 Important Notes

### API Credentials

- **Main Wallet Address**: Your master account address from Hyperliquid
- **API Key**: Public identifier for your API wallet (safe to share)
- **API Secret Key**: Private secret for your API wallet (NEVER share)

### Risk Warnings

- **Testnet First**: Always test thoroughly on testnet before mainnet
- **Real Money**: Mainnet involves real cryptocurrency trading
- **Market Risk**: Cryptocurrency trading involves significant risk
- **API Risk**: Secure your API keys and never share them
- **Strategy Risk**: Past performance doesn't guarantee future results

## 🔧 Troubleshooting

### Common Issues

1. **"Invalid API credentials"**
   - Verify wallet address format (0x...)
   - Check API key and secret are correct
   - Ensure API wallet is authorized

2. **"No pairs found"**
   - Check Hyperliquid connection
   - Verify exchange is accessible
   - Check pair filters in configuration

3. **"Insufficient balance"**
   - Check account balance in USDC
   - Verify stake amount vs. available balance
   - Check leverage settings

### Debug Mode

Add `--verbosity 3` to see detailed logs:
```bash
python -m freqtrade trade --config user_data/config_hyperliquid_testnet.json --verbosity 3
```

## 📈 Strategy Optimization

### Hyperparameter Optimization

```bash
# Run hyperopt to optimize strategy parameters
python -m freqtrade hyperopt --config user_data/config_hyperliquid_testnet.json --strategy MovingAverageCrossStrategy --epochs 100 --spaces buy sell
```

### Custom Modifications

The strategy is designed to be easily modified:
- Adjust MA periods in strategy file
- Modify risk parameters (stop loss, take profit)
- Add additional indicators
- Change entry/exit conditions

## 📞 Support

### Getting Help

1. **Check Logs**: Always check `user_data/logs/freqtrade.log` first
2. **Status Command**: Run `./configure.sh status` to check configuration
3. **Freqtrade Docs**: [Official Documentation](https://www.freqtrade.io/en/stable/)
4. **Hyperliquid Docs**: [Hyperliquid Documentation](https://hyperliquid.gitbook.io/)

### Development

This setup is based on:
- **Freqtrade**: 2024.11 with native Hyperliquid support
- **Python**: 3.11
- **Exchange**: Hyperliquid perpetual futures
- **Strategy**: Moving Average Crossover with risk management

---

**Disclaimer**: This software is for educational and informational purposes only. Cryptocurrency trading involves substantial risk of loss. Always do your own research and consider your financial situation before trading.