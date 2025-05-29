import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TrendingUp, TrendingDown, DollarSign, PieChart, BarChart3, Eye, EyeOff } from 'lucide-react';
import LoadingSpinner from './LoadingSpinner';

const Portfolio = () => {
  const [portfolio, setPortfolio] = useState(null);
  const [account, setAccount] = useState(null);
  const [orderHistory, setOrderHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showBalances, setShowBalances] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchPortfolioData();
    const interval = setInterval(fetchPortfolioData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchPortfolioData = async () => {
    try {
      setLoading(true);
      
      // Fetch portfolio data
      const portfolioResponse = await axios.get('/api/portfolio');
      if (portfolioResponse.data.success) {
        setPortfolio(portfolioResponse.data.data);
      }

      // Fetch account info
      const accountResponse = await axios.get('/api/account');
      if (accountResponse.data.success) {
        setAccount(accountResponse.data.data);
      }

      // Fetch order history
      const historyResponse = await axios.get('/api/orders/history?limit=20');
      if (historyResponse.data.success) {
        setOrderHistory(historyResponse.data.data);
      }

    } catch (error) {
      console.error('Error fetching portfolio data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return showBalances 
      ? `$${amount?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}`
      : '****';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'filled':
        return 'bg-green-900 text-green-300';
      case 'pending':
        return 'bg-yellow-900 text-yellow-300';
      case 'cancelled':
        return 'bg-red-900 text-red-300';
      default:
        return 'bg-gray-900 text-gray-300';
    }
  };

  if (loading && !portfolio) {
    return (
      <div className="p-6 flex items-center justify-center h-64">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">Portfolio</h1>
        <button
          onClick={() => setShowBalances(!showBalances)}
          className="flex items-center space-x-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
        >
          {showBalances ? <EyeOff size={20} /> : <Eye size={20} />}
          <span>{showBalances ? 'Hide' : 'Show'} Balances</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 bg-gray-800 p-1 rounded-lg">
        {['overview', 'positions', 'history'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === tab
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-700'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Account Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Account Value</p>
                  <p className="text-2xl font-bold text-white">
                    {formatCurrency(portfolio?.account_value)}
                  </p>
                </div>
                <DollarSign className="w-8 h-8 text-blue-400" />
              </div>
            </div>

            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Available Balance</p>
                  <p className="text-2xl font-bold text-white">
                    {formatCurrency(portfolio?.available_balance)}
                  </p>
                </div>
                <BarChart3 className="w-8 h-8 text-green-400" />
              </div>
            </div>

            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Margin Used</p>
                  <p className="text-2xl font-bold text-white">
                    {formatCurrency(portfolio?.margin_used)}
                  </p>
                </div>
                <PieChart className="w-8 h-8 text-orange-400" />
              </div>
            </div>

            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Total PnL</p>
                  <p className={`text-2xl font-bold ${
                    portfolio?.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {showBalances 
                      ? `${portfolio?.total_pnl >= 0 ? '+' : ''}${formatCurrency(portfolio?.total_pnl).replace('$', '')}`
                      : '****'
                    }
                  </p>
                </div>
                {portfolio?.total_pnl >= 0 ? 
                  <TrendingUp className="w-8 h-8 text-green-400" /> : 
                  <TrendingDown className="w-8 h-8 text-red-400" />
                }
              </div>
            </div>
          </div>

          {/* Account Details */}
          {account && (
            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
              <h2 className="text-xl font-bold text-white mb-4">Account Details</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold text-white mb-3">Account Information</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Address:</span>
                      <span className="text-white font-mono">
                        {account.address ? `${account.address.slice(0, 8)}...${account.address.slice(-8)}` : 'N/A'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Withdrawable:</span>
                      <span className="text-white">{formatCurrency(account.withdrawable)}</span>
                    </div>
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white mb-3">Margin Summary</h3>
                  <div className="space-y-2 text-sm">
                    {account.margin_summary && Object.entries(account.margin_summary).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="text-gray-400 capitalize">
                          {key.replace(/([A-Z])/g, ' $1').toLowerCase()}:
                        </span>
                        <span className="text-white">
                          {typeof value === 'number' ? formatCurrency(value) : value}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Positions Tab */}
      {activeTab === 'positions' && (
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h2 className="text-xl font-bold text-white mb-4">Current Positions</h2>
          
          {portfolio?.positions && portfolio.positions.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-gray-700">
                    <th className="pb-3 text-gray-400">Asset</th>
                    <th className="pb-3 text-gray-400">Side</th>
                    <th className="pb-3 text-gray-400">Size</th>
                    <th className="pb-3 text-gray-400">Entry Price</th>
                    <th className="pb-3 text-gray-400">Current Price</th>
                    <th className="pb-3 text-gray-400">Unrealized PnL</th>
                    <th className="pb-3 text-gray-400">Realized PnL</th>
                    <th className="pb-3 text-gray-400">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {portfolio.positions.map((position, index) => (
                    <tr key={index} className="border-b border-gray-700/50">
                      <td className="py-3 text-white font-semibold">{position.coin}</td>
                      <td className="py-3">
                        <span className={`px-2 py-1 rounded text-xs font-semibold ${
                          position.side === 'buy' 
                            ? 'bg-green-900 text-green-300' 
                            : 'bg-red-900 text-red-300'
                        }`}>
                          {position.side.toUpperCase()}
                        </span>
                      </td>
                      <td className="py-3 text-white">{position.size}</td>
                      <td className="py-3 text-white">${position.entry_price?.toLocaleString()}</td>
                      <td className="py-3 text-white">${position.current_price?.toLocaleString()}</td>
                      <td className={`py-3 font-semibold ${
                        position.unrealized_pnl >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {showBalances 
                          ? `${position.unrealized_pnl >= 0 ? '+' : ''}$${Math.abs(position.unrealized_pnl).toLocaleString()}`
                          : '****'
                        }
                      </td>
                      <td className={`py-3 font-semibold ${
                        position.realized_pnl >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {showBalances 
                          ? `${position.realized_pnl >= 0 ? '+' : ''}$${Math.abs(position.realized_pnl).toLocaleString()}`
                          : '****'
                        }
                      </td>
                      <td className="py-3 text-gray-400 text-sm">
                        {formatDate(position.created_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12">
              <PieChart className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400 text-lg">No active positions</p>
              <p className="text-gray-500 text-sm">Start trading to see your positions here</p>
            </div>
          )}
        </div>
      )}

      {/* History Tab */}
      {activeTab === 'history' && (
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h2 className="text-xl font-bold text-white mb-4">Order History</h2>
          
          {orderHistory.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-gray-700">
                    <th className="pb-3 text-gray-400">Asset</th>
                    <th className="pb-3 text-gray-400">Side</th>
                    <th className="pb-3 text-gray-400">Type</th>
                    <th className="pb-3 text-gray-400">Size</th>
                    <th className="pb-3 text-gray-400">Price</th>
                    <th className="pb-3 text-gray-400">Status</th>
                    <th className="pb-3 text-gray-400">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {orderHistory.map((order, index) => (
                    <tr key={index} className="border-b border-gray-700/50">
                      <td className="py-3 text-white font-semibold">{order.coin}</td>
                      <td className="py-3">
                        <span className={`px-2 py-1 rounded text-xs font-semibold ${
                          order.side === 'buy' 
                            ? 'bg-green-900 text-green-300' 
                            : 'bg-red-900 text-red-300'
                        }`}>
                          {order.side.toUpperCase()}
                        </span>
                      </td>
                      <td className="py-3 text-white capitalize">{order.order_type}</td>
                      <td className="py-3 text-white">{order.size}</td>
                      <td className="py-3 text-white">
                        {order.price ? `$${order.price.toLocaleString()}` : 'Market'}
                      </td>
                      <td className="py-3">
                        <span className={`px-2 py-1 rounded text-xs font-semibold ${getStatusColor(order.status)}`}>
                          {order.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="py-3 text-gray-400 text-sm">
                        {formatDate(order.created_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12">
              <BarChart3 className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400 text-lg">No order history</p>
              <p className="text-gray-500 text-sm">Your trading history will appear here</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Portfolio;