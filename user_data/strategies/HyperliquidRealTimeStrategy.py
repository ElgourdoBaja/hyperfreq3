# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement

import numpy as np
import pandas as pd
from pandas import DataFrame
from datetime import datetime
from typing import Optional
import requests

from freqtrade.strategy import IStrategy
from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,
                                IStrategy, IntParameter)


class HyperliquidRealTimeStrategy(IStrategy):
    """
    Real-Time Strategy for Hyperliquid - Works WITHOUT Historical Data
    
    This strategy bypasses Freqtrade's historical data requirements and uses 
    real-time Hyperliquid API calls for decision making, similar to Hypertrader-1.5
    """

    # Strategy interface version - allow new iterations of the strategy
    INTERFACE_VERSION = 3

    # Can this strategy go short?
    can_short = True

    # Optimal timeframe for the strategy
    timeframe = '1m'

    # Can this strategy use position stacking?
    position_stacking = False

    # These values can be overridden in the "ask_strategy" section in the config.
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 0  # NO HISTORICAL DATA REQUIRED!

    # Optional order type mapping.
    order_types = {
        'entry': 'market',  # Use market orders for faster execution
        'exit': 'market',
        'stoploss': 'market',
        'stoploss_on_exchange': False,  # Hyperliquid doesn't support this well
        'stoploss_on_exchange_interval': 60
    }

    # Optional order time in force.
    order_time_in_force = {
        'entry': 'GTC',
        'exit': 'GTC'
    }

    # Leverage to use (2x as specified)
    leverage_optimize = False
    leverage_num = DecimalParameter(1.0, 3.0, default=2.0, space='buy', optimize=leverage_optimize)

    # Strategy parameters - simplified for real-time operation
    price_change_threshold = DecimalParameter(0.005, 0.02, default=0.01, space="buy", optimize=False)  # 1% price change threshold

    # Stop loss and take profit percentages
    stoploss_percent = DecimalParameter(-0.15, -0.05, default=-0.10, space="sell", optimize=False)
    take_profit_percent = DecimalParameter(0.20, 0.50, default=0.30, space="sell", optimize=False)

    # ROI table - Take profit at 30% as specified
    minimal_roi = {
        "0": 0.30  # 30% take profit
    }

    # Optimal stoploss - 10% as specified
    stoploss = -0.10

    def leverage(self, pair: str, current_time: datetime, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag: Optional[str],
                 side: str, **kwargs) -> float:
        """Customize leverage for each new trade."""
        return self.leverage_num.value

    def get_hyperliquid_real_time_data(self, coin: str):
        """Get real-time data directly from Hyperliquid API (like Hypertrader-1.5)"""
        try:
            # Get current price from mainnet (more reliable than testnet)
            mids_response = requests.post(
                "https://api.hyperliquid.xyz/info",
                json={"type": "allMids"},
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if mids_response.status_code == 200:
                all_mids = mids_response.json()
                current_price = float(all_mids.get(coin, 0))
                
                return {
                    'price': current_price,
                    'timestamp': datetime.utcnow()
                }
            
            return None
        except Exception as e:
            print(f"Error fetching real-time data for {coin}: {e}")
            return None

    def informative_pairs(self):
        """Define additional, informative pair/interval combinations to be cached from the exchange."""
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        REAL-TIME STRATEGY: We don't rely on traditional indicators
        Instead, we'll use real-time API calls in the populate_entry_trend
        """
        
        # Add basic columns to prevent errors, but we won't use them for signals
        if len(dataframe) > 0:
            dataframe['volume_sma'] = dataframe['volume'].rolling(window=min(3, len(dataframe)), min_periods=1).mean()
            
            # Add simple price change calculation if we have enough data
            if len(dataframe) >= 2:
                dataframe['price_change'] = (dataframe['close'] - dataframe['close'].shift(1)) / dataframe['close'].shift(1)
            else:
                dataframe['price_change'] = 0
        else:
            # Empty dataframe fallback - create minimal structure
            dataframe['volume_sma'] = 0 if len(dataframe) == 0 else dataframe['volume']
            dataframe['price_change'] = 0

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        REAL-TIME ENTRY SIGNALS using direct Hyperliquid API calls
        This bypasses the need for historical candlestick data
        """
        
        # Initialize entry columns
        dataframe['enter_long'] = 0
        dataframe['enter_short'] = 0
        dataframe['enter_tag'] = ''
        
        if len(dataframe) == 0:
            return dataframe
        
        # Extract coin name from pair (e.g., 'BTC/USDC:USDC' -> 'BTC')
        pair = metadata.get('pair', '')
        coin = pair.split('/')[0] if '/' in pair else 'BTC'
        
        # Get real-time data from Hyperliquid
        real_time_data = self.get_hyperliquid_real_time_data(coin)
        
        if real_time_data and real_time_data['price'] > 0:
            current_price = real_time_data['price']
            
            # Get the last row index
            last_idx = len(dataframe) - 1
            
            if last_idx >= 0:
                # Compare real-time price with dataframe price
                dataframe_price = dataframe.iloc[last_idx]['close']
                
                # Calculate price difference
                if dataframe_price > 0:
                    price_diff_pct = (current_price - dataframe_price) / dataframe_price
                    
                    # ENTRY LOGIC: Based on real-time price momentum
                    # Long signal: Real-time price is significantly higher than last candle
                    if price_diff_pct > self.price_change_threshold.value:
                        dataframe.at[last_idx, 'enter_long'] = 1
                        dataframe.at[last_idx, 'enter_tag'] = 'realtime_momentum_long'
                        print(f"🟢 LONG SIGNAL: {coin} real-time price ${current_price:.2f} vs candle ${dataframe_price:.2f} (+{price_diff_pct:.2%})")
                    
                    # Short signal: Real-time price is significantly lower than last candle  
                    elif price_diff_pct < -self.price_change_threshold.value:
                        dataframe.at[last_idx, 'enter_short'] = 1
                        dataframe.at[last_idx, 'enter_tag'] = 'realtime_momentum_short'
                        print(f"🔴 SHORT SIGNAL: {coin} real-time price ${current_price:.2f} vs candle ${dataframe_price:.2f} ({price_diff_pct:.2%})")

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Real-time exit signals - also using direct API calls
        """
        
        # Initialize exit columns
        dataframe['exit_long'] = 0
        dataframe['exit_short'] = 0 
        dataframe['exit_tag'] = ''
        
        if len(dataframe) == 0:
            return dataframe
        
        # Extract coin name from pair
        pair = metadata.get('pair', '')
        coin = pair.split('/')[0] if '/' in pair else 'BTC'
        
        # Get real-time data
        real_time_data = self.get_hyperliquid_real_time_data(coin)
        
        if real_time_data and real_time_data['price'] > 0:
            current_price = real_time_data['price']
            last_idx = len(dataframe) - 1
            
            if last_idx >= 0:
                dataframe_price = dataframe.iloc[last_idx]['close']
                
                if dataframe_price > 0:
                    price_diff_pct = (current_price - dataframe_price) / dataframe_price
                    
                    # EXIT LOGIC: Reverse momentum signals
                    # Exit long when price drops significantly
                    if price_diff_pct < -self.price_change_threshold.value * 0.5:  # Half the entry threshold
                        dataframe.at[last_idx, 'exit_long'] = 1
                        dataframe.at[last_idx, 'exit_tag'] = 'realtime_momentum_exit_long'
                    
                    # Exit short when price rises significantly
                    elif price_diff_pct > self.price_change_threshold.value * 0.5:
                        dataframe.at[last_idx, 'exit_short'] = 1
                        dataframe.at[last_idx, 'exit_tag'] = 'realtime_momentum_exit_short'

        return dataframe

    def custom_exit(self, pair: str, trade, current_time: datetime, current_rate: float,
                    current_profit: float, **kwargs) -> Optional[str]:
        """Custom exit signal logic"""
        
        # Take profit at 30% as specified
        if current_profit >= self.take_profit_percent.value:
            return f'take_profit_{self.take_profit_percent.value*100:.0f}_percent'
        
        # Stop loss at -10% as specified
        if current_profit <= self.stoploss_percent.value:
            return f'stop_loss_{abs(self.stoploss_percent.value)*100:.0f}_percent'
        
        return None

    def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
                           time_in_force: str, current_time: datetime, entry_tag: Optional[str],
                           side: str, **kwargs) -> bool:
        """Called right before placing a entry order."""
        
        # Double-check with real-time data before entry
        coin = pair.split('/')[0] if '/' in pair else 'BTC'
        real_time_data = self.get_hyperliquid_real_time_data(coin)
        
        if real_time_data and real_time_data['price'] > 0:
            real_time_price = real_time_data['price']
            
            # Ensure the price hasn't moved too much against us
            price_diff_pct = abs(real_time_price - rate) / rate
            
            if price_diff_pct < 0.02:  # Allow 2% price difference
                print(f"✅ CONFIRMING {side.upper()} ENTRY: {pair} at ${rate:.2f} (real-time: ${real_time_price:.2f})")
                return True
            else:
                print(f"❌ REJECTING {side.upper()} ENTRY: {pair} - price moved too much. Order: ${rate:.2f} vs Real-time: ${real_time_price:.2f}")
                return False
        
        # If we can't get real-time data, proceed with caution
        print(f"⚠️  PROCEEDING WITHOUT REAL-TIME CONFIRMATION: {pair} {side.upper()} at ${rate:.2f}")
        return True

    def confirm_trade_exit(self, pair: str, trade, order_type: str, amount: float,
                          rate: float, time_in_force: str, exit_reason: str,
                          current_time: datetime, **kwargs) -> bool:
        """Called right before placing a regular exit order."""
        return True