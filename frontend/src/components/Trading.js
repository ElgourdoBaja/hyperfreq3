import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TrendingUp, TrendingDown, DollarSign, Clock, AlertCircle } from 'lucide-react';
import LoadingSpinner from './LoadingSpinner';

const Trading = () => {
  const [orderForm, setOrderForm] = useState({
    coin: 'BTC',
    side: 'buy',
    orderType: 'limit',
    size: '',
    price: '',
    reduceOnly: false
  });
  const [marketData, setMarketData] = useState({});
  const [orderBook, setOrderBook] = useState(null);
  const [openOrders, setOpenOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const coins = ['BTC', 'ETH', 'SOL', 'AVAX', 'MATIC', 'LINK'];

  useEffect(() => {
    fetchTradingData();
    const interval = setInterval(fetchTradingData, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, [orderForm.coin]);

  const fetchTradingData = async () => {
    try {
      setLoading(true);
      
      // Fetch market data
      const marketResponse = await axios.get(`/api/market/${orderForm.coin}`);
      if (marketResponse.data.success) {
        setMarketData(marketResponse.data.data);
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
      const price = orderForm.side === 'buy' ? marketData.ask : marketData.bid;
      setOrderForm(prev => ({
        ...prev,
        price: price?.toFixed(2) || ''
      }));
    }
  };

  const handleSubmitOrder = async (e) => {
    e.preventDefault();
    
    if (!orderForm.size || (!orderForm.price && orderForm.orderType === 'limit')) {
      setMessage({ type: 'error', text: 'Please fill in all required fields' });
      return;
    }

    try {
      setSubmitLoading(true);
      setMessage(null);

      const orderRequest = {
        coin: orderForm.coin,
        is_buy: orderForm.side === 'buy',
        sz: parseFloat(orderForm.size),
        limit_px: orderForm.orderType === 'limit' ? parseFloat(orderForm.price) : null,
        order_type: orderForm.orderType,
        reduce_only: orderForm.reduceOnly
      };

      const response = await axios.post('/api/orders', orderRequest);
      
      if (response.data.success) {
        setMessage({ type: 'success', text: 'Order placed successfully!' });
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

  const formatPrice = (price) => {
    return `$${price?.toLocaleString('en-US', { 
      minimumFractionDigits: 2, 
      maximumFractionDigits: 2 
    }) || '0.00'}`;
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">Trading</h1>
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <p className="text-sm text-gray-400">Current Price</p>
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
        {/* Order Form */}
        <div className="lg:col-span-1">
          <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-4">Place Order</h2>
            
            <form onSubmit={handleSubmitOrder} className="space-y-4">
              {/* Coin Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Asset
                </label>
                <select
                  value={orderForm.coin}
                  onChange={(e) => handleInputChange('coin', e.target.value)}
                  className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-400"
                >
                  {coins.map(coin => (
                    <option key={coin} value={coin}>{coin}</option>
                  ))}
                </select>
              </div>

              {/* Side Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Side
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => handleInputChange('side', 'buy')}
                    className={`py-2 px-4 rounded font-medium transition-colors ${
                      orderForm.side === 'buy'
                        ? 'bg-green-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    Buy
                  </button>
                  <button
                    type="button"
                    onClick={() => handleInputChange('side', 'sell')}
                    className={`py-2 px-4 rounded font-medium transition-colors ${
                      orderForm.side === 'sell'
                        ? 'bg-red-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    Sell
                  </button>
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
                  <option value="limit">Limit</option>
                  <option value="market">Market</option>
                </select>
              </div>

              {/* Size */}
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Size
                </label>
                <input
                  type="number"
                  step="0.001"
                  value={orderForm.size}
                  onChange={(e) => handleInputChange('size', e.target.value)}
                  placeholder="0.000"
                  className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-400"
                />
              </div>

              {/* Price (for limit orders) */}
              {orderForm.orderType === 'limit' && (
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    Price
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

              {/* Reduce Only */}
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

              {/* Submit Button */}
              <button
                type="submit"
                disabled={submitLoading}
                className={`w-full py-3 px-4 rounded font-medium transition-colors ${
                  orderForm.side === 'buy'
                    ? 'bg-green-600 hover:bg-green-700 text-white'
                    : 'bg-red-600 hover:bg-red-700 text-white'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {submitLoading ? (
                  <LoadingSpinner size="small" />
                ) : (
                  `${orderForm.side.toUpperCase()} ${orderForm.coin}`
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
                  <h3 className="text-sm font-medium text-red-400 mb-2">Asks</h3>
                  <div className="space-y-1">
                    {orderBook.asks?.slice(0, 10).map((level, index) => (
                      <div key={index} className="flex justify-between text-sm">
                        <span className="text-red-400">{formatPrice(level.price)}</span>
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
                </div>

                {/* Bids */}
                <div>
                  <h3 className="text-sm font-medium text-green-400 mb-2">Bids</h3>
                  <div className="space-y-1">
                    {orderBook.bids?.slice(0, 10).map((level, index) => (
                      <div key={index} className="flex justify-between text-sm">
                        <span className="text-green-400">{formatPrice(level.price)}</span>
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
                        <span className="font-semibold text-white">{order.coin}</span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          order.side === 'buy' 
                            ? 'bg-green-900 text-green-300'
                            : 'bg-red-900 text-red-300'
                        }`}>
                          {order.side.toUpperCase()}
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