import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TrendingUp, TrendingDown, DollarSign, Clock, AlertCircle, Target, Zap } from 'lucide-react';
import LoadingSpinner from './LoadingSpinner';

const Trading = () => {
  const [orderForm, setOrderForm] = useState({
    coin: 'BTC',
    side: 'long', // Changed from 'buy' to 'long' for perps
    orderType: 'limit',
    size: '',
    price: '',
    leverage: 1,
    reduceOnly: false,
    postOnly: false
  });
  const [marketData, setMarketData] = useState({});
  const [orderBook, setOrderBook] = useState(null);
  const [openOrders, setOpenOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [availableCoins, setAvailableCoins] = useState([]);

  // Top 20 most popular perp pairs for quick access
  const popularPairs = ['BTC', 'ETH', 'SOL', 'AVAX', 'MATIC', 'DOGE', 'LINK', 'UNI', 'AAVE', 'ARB', 'OP', 'LTC', 'XRP', 'BCH', 'APT', 'SUI', 'SEI', 'INJ', 'TIA', 'NEAR'];

  useEffect(() => {
    fetchAvailableCoins();
    fetchTradingData();
    const interval = setInterval(fetchTradingData, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, [orderForm.coin]);

  const fetchAvailableCoins = async () => {
    try {
      const response = await axios.get('/api/coins');
      if (response.data.success) {
        setAvailableCoins(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching available coins:', error);
    }
  };

  const fetchTradingData = async () => {
    try {
      setLoading(true);
      
      // Fetch market data
      const marketResponse = await axios.get(`/api/market/${orderForm.coin}`);
      if (marketResponse.data.success) {
        setMarketData(marketResponse.data.data);
        
        // Auto-fill price for market orders
        if (orderForm.orderType === 'market') {
          const price = orderForm.side === 'long' ? marketResponse.data.data.ask : marketResponse.data.data.bid;
          setOrderForm(prev => ({
            ...prev,
            price: price?.toFixed(2) || ''
          }));
        }
      }

      // Fetch order book
      const orderBookResponse = await axios.get(`/api/orderbook/${orderForm.coin}`);
      if (orderBookResponse.data.success) {
        setOrderBook(orderBookResponse.data.data);
      }

      // Fetch open orders
      const ordersResponse = await axios.get('/api/orders/open');
      if (ordersResponse.data.success) {
        setOpenOrders(ordersResponse.data.data);
      }

    } catch (error) {
      console.error('Error fetching trading data:', error);
      setMessage({ type: 'error', text: 'Failed to fetch trading data' });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setOrderForm(prev => ({
      ...prev,
      [field]: value
    }));

    // Auto-fill price for market orders
    if (field === 'orderType' && value === 'market') {
      const price = orderForm.side === 'long' ? marketData.ask : marketData.bid;
      setOrderForm(prev => ({
        ...prev,
        price: price?.toFixed(2) || ''
      }));
    }

    // Auto-fill price when switching sides
    if (field === 'side') {
      const price = value === 'long' ? marketData.ask : marketData.bid;
      if (orderForm.orderType === 'market') {
        setOrderForm(prev => ({
          ...prev,
          price: price?.toFixed(2) || ''
        }));
      }
    }
  };

  const handleSubmitOrder = async (e) => {
    e.preventDefault();
    
    if (!orderForm.size || (!orderForm.price && orderForm.orderType === 'limit')) {
      setMessage({ type: 'error', text: 'Please fill in all required fields' });
      return;
    }

    if (orderForm.leverage < 1 || orderForm.leverage > getMaxLeverage()) {
      setMessage({ type: 'error', text: `Leverage must be between 1x and ${getMaxLeverage()}x` });
      return;
    }

    try {
      setSubmitLoading(true);
      setMessage(null);

      const orderRequest = {
        coin: orderForm.coin,
        is_buy: orderForm.side === 'long',
        sz: parseFloat(orderForm.size),
        limit_px: orderForm.orderType === 'limit' ? parseFloat(orderForm.price) : null,
        order_type: orderForm.orderType,
        reduce_only: orderForm.reduceOnly,
        leverage: orderForm.leverage
      };

      const response = await axios.post('/api/orders', orderRequest);
      
      if (response.data.success) {
        setMessage({ 
          type: 'success', 
          text: `${orderForm.side.toUpperCase()} order placed successfully! Size: ${orderForm.size} ${orderForm.coin} @ ${orderForm.leverage}x leverage` 
        });
        setOrderForm(prev => ({ ...prev, size: '', price: '' }));
        fetchTradingData(); // Refresh data
      } else {
        setMessage({ type: 'error', text: response.data.message || 'Failed to place order' });
      }

    } catch (error) {
      console.error('Error placing order:', error);
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Failed to place order' 
      });
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleCancelOrder = async (coin, oid) => {
    try {
      const response = await axios.delete(`/api/orders/${coin}/${oid}`);
      if (response.data.success) {
        setMessage({ type: 'success', text: 'Order cancelled successfully!' });
        fetchTradingData(); // Refresh data
      } else {
        setMessage({ type: 'error', text: 'Failed to cancel order' });
      }
    } catch (error) {
      console.error('Error cancelling order:', error);
      setMessage({ type: 'error', text: 'Failed to cancel order' });
    }
  };

  const getMaxLeverage = () => {
    const coin = availableCoins.find(c => c.symbol === orderForm.coin);
    return coin?.maxLeverage || 1;
  };

  const calculateNotionalValue = () => {
    const size = parseFloat(orderForm.size) || 0;
    const price = parseFloat(orderForm.price) || marketData.price || 0;
    return size * price;
  };

  const calculateMarginRequired = () => {
    const notional = calculateNotionalValue();
    return notional / orderForm.leverage;
  };

  const formatPrice = (price) => {
    return `$${price?.toLocaleString('en-US', { 
      minimumFractionDigits: 2, 
      maximumFractionDigits: 2 
    }) || '0.00'}`;
  };

  const handleQuickFill = (percentage) => {
    // In a real implementation, this would use actual account balance
    const mockBalance = 10000; // $10,000 mock balance
    const price = parseFloat(orderForm.price) || marketData.price || 0;
    const availableForPosition = (mockBalance * percentage / 100) * orderForm.leverage;
    const size = availableForPosition / price;
    
    setOrderForm(prev => ({
      ...prev,
      size: size.toFixed(6)
    }));
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">Perpetual Futures Trading</h1>
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <p className="text-sm text-gray-400">Mark Price</p>
            <p className="text-lg font-bold text-white">
              {formatPrice(marketData.price)}
            </p>
          </div>
          <div className={`px-3 py-1 rounded ${
            marketData.change_24h >= 0 ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'
          }`}>
            {marketData.change_24h >= 0 ? '+' : ''}{marketData.change_24h?.toFixed(2)}%
          </div>
        </div>
      </div>

      {/* Popular Pairs Quick Access */}
      <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
        <h3 className="text-sm font-medium text-gray-400 mb-2">Popular Pairs</h3>
        <div className="flex flex-wrap gap-2">
          {popularPairs.map(pair => (
            <button
              key={pair}
              onClick={() => handleInputChange('coin', pair)}
              className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                orderForm.coin === pair
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {pair}
            </button>
          ))}
        </div>
      </div>

      {/* Message Display */}
      {message && (
        <div className={`p-4 rounded-lg flex items-center space-x-2 ${
          message.type === 'success' 
            ? 'bg-green-900 text-green-300 border border-green-700' 
            : 'bg-red-900 text-red-300 border border-red-700'
        }`}>
          <AlertCircle size={20} />
          <span>{message.text}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Long/Short Order Form */}
        <div className="lg:col-span-1">
          <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center">
              <Target className="w-5 h-5 mr-2" />
              Place Order
            </h2>
            
            <form onSubmit={handleSubmitOrder} className="space-y-4">
              {/* Asset Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Perpetual Contract
                </label>
                <select
                  value={orderForm.coin}
                  onChange={(e) => handleInputChange('coin', e.target.value)}
                  className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-400"
                >
                  {availableCoins.map(coin => (
                    <option key={coin.symbol} value={coin.symbol}>
                      {coin.symbol}-PERP (Max: {coin.maxLeverage}x)
                    </option>
                  ))}
                </select>
              </div>

              {/* Long/Short Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Position Direction
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => handleInputChange('side', 'long')}
                    className={`py-3 px-4 rounded font-medium transition-colors flex items-center justify-center ${
                      orderForm.side === 'long'
                        ? 'bg-green-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    <TrendingUp size={16} className="mr-2" />
                    LONG
                  </button>
                  <button
                    type="button"
                    onClick={() => handleInputChange('side', 'short')}
                    className={`py-3 px-4 rounded font-medium transition-colors flex items-center justify-center ${
                      orderForm.side === 'short'
                        ? 'bg-red-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    <TrendingDown size={16} className="mr-2" />
                    SHORT
                  </button>
                </div>
              </div>

              {/* Leverage */}
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Leverage: {orderForm.leverage}x (Max: {getMaxLeverage()}x)
                </label>
                <input
                  type="range"
                  min="1"
                  max={getMaxLeverage()}
                  step="1"
                  value={orderForm.leverage}
                  onChange={(e) => handleInputChange('leverage', parseInt(e.target.value))}
                  className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>1x</span>
                  <span>{getMaxLeverage()}x</span>
                </div>
              </div>

              {/* Order Type */}
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Order Type
                </label>
                <select
                  value={orderForm.orderType}
                  onChange={(e) => handleInputChange('orderType', e.target.value)}
                  className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-400"
                >
                  <option value="limit">Limit Order</option>
                  <option value="market">Market Order</option>
                </select>
              </div>

              {/* Size */}
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Size ({orderForm.coin})
                </label>
                <input
                  type="number"
                  step="0.000001"
                  value={orderForm.size}
                  onChange={(e) => handleInputChange('size', e.target.value)}
                  placeholder="0.000000"
                  className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-400"
                />
                
                {/* Quick Fill Buttons */}
                <div className="flex space-x-1 mt-2">
                  {[25, 50, 75, 100].map(percentage => (
                    <button
                      key={percentage}
                      type="button"
                      onClick={() => handleQuickFill(percentage)}
                      className="flex-1 py-1 px-2 text-xs bg-gray-600 hover:bg-gray-500 rounded transition-colors"
                    >
                      {percentage}%
                    </button>
                  ))}
                </div>
              </div>

              {/* Price (for limit orders) */}
              {orderForm.orderType === 'limit' && (
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    Price (USD)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={orderForm.price}
                    onChange={(e) => handleInputChange('price', e.target.value)}
                    placeholder="0.00"
                    className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-400"
                  />
                </div>
              )}

              {/* Order Options */}
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="reduceOnly"
                    checked={orderForm.reduceOnly}
                    onChange={(e) => handleInputChange('reduceOnly', e.target.checked)}
                    className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="reduceOnly" className="text-sm text-gray-400">
                    Reduce Only
                  </label>
                </div>
                
                {orderForm.orderType === 'limit' && (
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="postOnly"
                      checked={orderForm.postOnly}
                      onChange={(e) => handleInputChange('postOnly', e.target.checked)}
                      className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
                    />
                    <label htmlFor="postOnly" className="text-sm text-gray-400">
                      Post Only
                    </label>
                  </div>
                )}
              </div>

              {/* Order Summary */}
              {orderForm.size && orderForm.price && (
                <div className="p-3 bg-gray-700 rounded space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Notional Value:</span>
                    <span className="text-white">{formatPrice(calculateNotionalValue())}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Margin Required:</span>
                    <span className="text-white">{formatPrice(calculateMarginRequired())}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Leverage:</span>
                    <span className="text-white">{orderForm.leverage}x</span>
                  </div>
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={submitLoading}
                className={`w-full py-3 px-4 rounded font-medium transition-colors flex items-center justify-center ${
                  orderForm.side === 'long'
                    ? 'bg-green-600 hover:bg-green-700 text-white'
                    : 'bg-red-600 hover:bg-red-700 text-white'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {submitLoading ? (
                  <LoadingSpinner size="small" />
                ) : (
                  <>
                    <Zap size={16} className="mr-2" />
                    {orderForm.side.toUpperCase()} {orderForm.coin}-PERP
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Order Book */}
        <div className="lg:col-span-1">
          <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-4">Order Book</h2>
            
            {loading ? (
              <div className="flex justify-center py-8">
                <LoadingSpinner />
              </div>
            ) : orderBook ? (
              <div className="space-y-4">
                {/* Asks */}
                <div>
                  <h3 className="text-sm font-medium text-red-400 mb-2">Asks (Resistance)</h3>
                  <div className="space-y-1">
                    {orderBook.asks?.slice(0, 10).map((level, index) => (
                      <div key={index} className="flex justify-between text-sm hover:bg-red-900/20 p-1 rounded cursor-pointer"
                           onClick={() => orderForm.orderType === 'limit' && handleInputChange('price', level.price.toString())}>
                        <span className="text-red-400 font-mono">{formatPrice(level.price)}</span>
                        <span className="text-gray-400">{level.size}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Current Price */}
                <div className="text-center py-2 border-t border-b border-gray-700">
                  <span className="text-lg font-bold text-white">
                    {formatPrice(marketData.price)}
                  </span>
                  <p className="text-xs text-gray-400">Mark Price</p>
                </div>

                {/* Bids */}
                <div>
                  <h3 className="text-sm font-medium text-green-400 mb-2">Bids (Support)</h3>
                  <div className="space-y-1">
                    {orderBook.bids?.slice(0, 10).map((level, index) => (
                      <div key={index} className="flex justify-between text-sm hover:bg-green-900/20 p-1 rounded cursor-pointer"
                           onClick={() => orderForm.orderType === 'limit' && handleInputChange('price', level.price.toString())}>
                        <span className="text-green-400 font-mono">{formatPrice(level.price)}</span>
                        <span className="text-gray-400">{level.size}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-gray-400 text-center py-8">No order book data available</p>
            )}
          </div>
        </div>

        {/* Open Orders */}
        <div className="lg:col-span-1">
          <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-4">Open Orders</h2>
            
            {loading ? (
              <div className="flex justify-center py-8">
                <LoadingSpinner />
              </div>
            ) : openOrders.length > 0 ? (
              <div className="space-y-3">
                {openOrders.map((order, index) => (
                  <div key={index} className="p-3 bg-gray-700 rounded border border-gray-600">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold text-white">{order.coin}-PERP</span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          order.side === 'buy' 
                            ? 'bg-green-900 text-green-300'
                            : 'bg-red-900 text-red-300'
                        }`}>
                          {order.side === 'buy' ? 'LONG' : 'SHORT'}
                        </span>
                      </div>
                      <button
                        onClick={() => handleCancelOrder(order.coin, order.oid)}
                        className="text-red-400 hover:text-red-300 text-sm"
                      >
                        Cancel
                      </button>
                    </div>
                    <div className="text-sm text-gray-400">
                      <p>Size: {order.size}</p>
                      {order.price && <p>Price: {formatPrice(order.price)}</p>}
                      <p>Type: {order.order_type}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-400 text-center py-8">No open orders</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Trading;