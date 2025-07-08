# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401

import numpy as np
import pandas as pd
from pandas import DataFrame
from datetime import datetime
from typing import Optional

from freqtrade.strategy import IStrategy
from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,
                                IStrategy, IntParameter)


class MovingAverageCrossStrategy(IStrategy):
    """
    Moving Average Crossover Strategy for Hyperliquid
    
    This strategy uses a simple moving average crossover approach:
    - Buy signal when fast MA crosses above slow MA
    - Sell signal when fast MA crosses below slow MA
    - Includes stop loss (10%) and take profit (30%) as requested
    - Uses 2x leverage as specified
    - Position size of 10.00 as configured in config
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
    startup_candle_count: int = 30

    # Optional order type mapping.
    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'limit',
        'stoploss_on_exchange': True,
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

    # Strategy parameters
    # Moving average periods
    fast_ma_period = IntParameter(5, 20, default=10, space="buy", optimize=True)
    slow_ma_period = IntParameter(20, 50, default=20, space="buy", optimize=True)

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
        """
        Customize leverage for each new trade. This method is only called in futures mode.
        """
        return self.leverage_num.value

    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        These pairs will NOT be traded, unless they are also specified in the pair_whitelist.
        """
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds several different TA indicators to the given DataFrame

        Performance Note: For the best performance be frugal on the number of indicators
        you are using. Let uncomment only the indicator you are using in your strategies
        or your hyperopt configuration, otherwise you will waste your memory and CPU usage.
        """

        # Simple Moving Averages (using pandas instead of TA-Lib since we don't have it installed)
        dataframe['sma_fast'] = dataframe['close'].rolling(window=self.fast_ma_period.value).mean()
        dataframe['sma_slow'] = dataframe['close'].rolling(window=self.slow_ma_period.value).mean()

        # Volume indicators
        dataframe['volume_sma'] = dataframe['volume'].rolling(window=20).mean()

        # RSI for additional filtering (using pandas calculation)
        delta = dataframe['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        dataframe['rsi'] = 100 - (100 / (1 + rs))

        # Simple MACD calculation
        ema_fast = dataframe['close'].ewm(span=12).mean()
        ema_slow = dataframe['close'].ewm(span=26).mean()
        dataframe['macd'] = ema_fast - ema_slow
        dataframe['macd_signal'] = dataframe['macd'].ewm(span=9).mean()

        # Bollinger Bands for volatility awareness
        bb_period = 20
        bb_std = 2
        dataframe['bb_middle'] = dataframe['close'].rolling(window=bb_period).mean()
        bb_std_dev = dataframe['close'].rolling(window=bb_period).std()
        dataframe['bb_upper'] = dataframe['bb_middle'] + (bb_std_dev * bb_std)
        dataframe['bb_lower'] = dataframe['bb_middle'] - (bb_std_dev * bb_std)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the entry signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with entry columns populated
        """
        
        # Long entry conditions
        dataframe.loc[
            (
                # Moving average crossover - fast MA crosses above slow MA
                (dataframe['sma_fast'] > dataframe['sma_slow']) &
                (dataframe['sma_fast'].shift(1) <= dataframe['sma_slow'].shift(1)) &
                
                # Volume confirmation - current volume should be above average
                (dataframe['volume'] > dataframe['volume_sma']) &
                
                # RSI not overbought
                (dataframe['rsi'] < 70) &
                
                # MACD confirmation - MACD line above signal line
                (dataframe['macd'] > dataframe['macd_signal']) &
                
                # Price above middle Bollinger Band (trend confirmation)
                (dataframe['close'] > dataframe['bb_middle'])
            ),
            ['enter_long', 'enter_tag']] = (1, 'ma_cross_long')

        # Short entry conditions
        dataframe.loc[
            (
                # Moving average crossover - fast MA crosses below slow MA
                (dataframe['sma_fast'] < dataframe['sma_slow']) &
                (dataframe['sma_fast'].shift(1) >= dataframe['sma_slow'].shift(1)) &
                
                # Volume confirmation - current volume should be above average
                (dataframe['volume'] > dataframe['volume_sma']) &
                
                # RSI not oversold
                (dataframe['rsi'] > 30) &
                
                # MACD confirmation - MACD line below signal line
                (dataframe['macd'] < dataframe['macd_signal']) &
                
                # Price below middle Bollinger Band (trend confirmation)
                (dataframe['close'] < dataframe['bb_middle'])
            ),
            ['enter_short', 'enter_tag']] = (1, 'ma_cross_short')

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the exit signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with exit columns populated
        """
        
        # Long exit conditions
        dataframe.loc[
            (
                # Exit when fast MA crosses below slow MA
                (dataframe['sma_fast'] < dataframe['sma_slow']) &
                (dataframe['sma_fast'].shift(1) >= dataframe['sma_slow'].shift(1))
            ) |
            (
                # Or when RSI is overbought
                (dataframe['rsi'] > 80)
            ) |
            (
                # Or when MACD turns bearish
                (dataframe['macd'] < dataframe['macd_signal']) &
                (dataframe['macd'].shift(1) >= dataframe['macd_signal'].shift(1))
            ),
            ['exit_long', 'exit_tag']] = (1, 'ma_cross_exit_long')

        # Short exit conditions
        dataframe.loc[
            (
                # Exit when fast MA crosses above slow MA
                (dataframe['sma_fast'] > dataframe['sma_slow']) &
                (dataframe['sma_fast'].shift(1) <= dataframe['sma_slow'].shift(1))
            ) |
            (
                # Or when RSI is oversold
                (dataframe['rsi'] < 20)
            ) |
            (
                # Or when MACD turns bullish
                (dataframe['macd'] > dataframe['macd_signal']) &
                (dataframe['macd'].shift(1) <= dataframe['macd_signal'].shift(1))
            ),
            ['exit_short', 'exit_tag']] = (1, 'ma_cross_exit_short')

        return dataframe

    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: datetime,
                        current_rate: float, current_profit: float, **kwargs) -> float:
        """
        Custom stoploss logic, returning the new distance relative to current_rate (as ratio).
        e.g. returning -0.05 would create a stoploss 5% below current_rate.
        The custom stoploss can never be below self.stoploss, which serves as a hard maximum loss.

        For full documentation please go to https://www.freqtrade.io/en/latest/strategy-advanced/
        
        When not implemented by a strategy, returns the initial stoploss value
        Only called when use_custom_stoploss is set to True.
        """
        
        # Use the configured stop loss percentage
        return self.stoploss_percent.value

    def custom_exit(self, pair: str, trade: 'Trade', current_time: datetime, current_rate: float,
                    current_profit: float, **kwargs) -> Optional[str]:
        """
        Custom exit signal logic indicating that specified position should be sold.
        """
        
        # Take profit at 30% as specified
        if current_profit >= self.take_profit_percent.value:
            return 'take_profit_30_percent'
        
        # Additional exit logic could be added here
        return None

    def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
                           time_in_force: str, current_time: datetime, entry_tag: Optional[str],
                           side: str, **kwargs) -> bool:
        """
        Called right before placing a entry order.
        Timing for this function is critical, so avoid doing heavy computations or
        network requests in this method.

        For full documentation please go to https://www.freqtrade.io/en/latest/strategy-advanced/

        When not implemented by a strategy, returns True (always confirming).

        :param pair: Pair that's about to be traded.
        :param order_type: Order type (as configured in order_types). usually limit or market.
        :param amount: Amount in target (base) currency that's going to be traded.
        :param rate: Rate that's going to be used when using limit orders
        :param time_in_force: Time in force. Defaults to GTC (Good-til-cancelled).
        :param current_time: datetime object, containing the current datetime
        :param entry_tag: Optional entry_tag (buy_tag) if provided with the buy signal.
        :param side: 'long' or 'short' - indicating the direction of the proposed trade
        :param **kwargs: Ensure to keep this here so updates to this won't break your strategy.
        :return bool: When True is returned, then the buy-order is placed on the exchange.
            False aborts the process
        """
        return True

    def confirm_trade_exit(self, pair: str, trade: 'Trade', order_type: str, amount: float,
                          rate: float, time_in_force: str, exit_reason: str,
                          current_time: datetime, **kwargs) -> bool:
        """
        Called right before placing a regular exit order.
        Timing for this function is critical, so avoid doing heavy computations or
        network requests in this method.

        For full documentation please go to https://www.freqtrade.io/en/latest/strategy-advanced/

        When not implemented by a strategy, returns True (always confirming).

        :param pair: Pair for trade that's about to be exited.
        :param trade: trade object.
        :param order_type: Order type (as configured in order_types). usually limit or market.
        :param amount: Amount in base currency.
        :param rate: Rate that's going to be used when using limit orders
        :param time_in_force: Time in force. Defaults to GTC (Good-til-cancelled).
        :param exit_reason: Exit reason.
            Can be any of ['roi', 'stop_loss', 'stoploss_on_exchange', 'trailing_stop_loss',
                           'exit_signal', 'force_exit', 'emergency_exit']
        :param current_time: datetime object, containing the current datetime
        :param **kwargs: Ensure to keep this here so updates to this won't break your strategy.
        :return bool: When True, then the exit-order is placed on the exchange.
            False aborts the process
        """
        return True