import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TrendingUp, TrendingDown, DollarSign, Activity, Eye, EyeOff } from 'lucide-react';
import LoadingSpinner from './LoadingSpinner';
import MarketChart from './MarketChart';

const Dashboard = () => {
  const [portfolio, setPortfolio] = useState(null);
  const [marketData, setMarketData] = useState({});
  const [loading, setLoading] = useState(true);
  const [showBalances, setShowBalances] = useState(true);
  const [selectedCoin, setSelectedCoin] = useState('BTC');

  const coins = ['BTC', 'ETH', 'SOL', 'AVAX'];

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch portfolio data
      const portfolioResponse = await axios.get('/api/portfolio');
      if (portfolioResponse.data.success) {
        setPortfolio(portfolioResponse.data.data);
      }

      // Fetch market data for multiple coins
      try {
        const marketDataPromises = coins.map(async coin => {
          try {
            const res = await axios.get(`/api/market/${coin}`);
            return { coin, data: res.data.success ? res.data.data : null };
          } catch (error) {
            console.warn(`Failed to fetch market data for ${coin}:`, error);
            return { coin, data: null };
          }
        });
        
        const marketResults = await Promise.all(marketDataPromises);
        const marketDataMap = {};
        marketResults.forEach(result => {
          if (result.data) {
            marketDataMap[result.coin] = result.data;
          }
        });
        setMarketData(marketDataMap);
      } catch (error) {
        console.warn('Error fetching market data:', error);
        // Don't fail the entire component if market data fails
      }

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return showBalances 
      ? `$${amount?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}`
      : '****';
  };

  const formatPercentage = (value) => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value?.toFixed(2) || '0.00'}%`;
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
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <button
          onClick={() => setShowBalances(!showBalances)}
          className="flex items-center space-x-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
        >
          {showBalances ? <EyeOff size={20} /> : <Eye size={20} />}
          <span>{showBalances ? 'Hide' : 'Show'} Balances</span>
        </button>
      </div>

      {/* Portfolio Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Value</p>
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
            <Activity className="w-8 h-8 text-green-400" />
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

        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Daily PnL</p>
              <p className={`text-2xl font-bold ${
                portfolio?.daily_pnl >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {showBalances 
                  ? `${portfolio?.daily_pnl >= 0 ? '+' : ''}${formatCurrency(portfolio?.daily_pnl).replace('$', '')}` 
                  : '****'
                }
              </p>
            </div>
            {portfolio?.daily_pnl >= 0 ? 
              <TrendingUp className="w-8 h-8 text-green-400" /> : 
              <TrendingDown className="w-8 h-8 text-red-400" />
            }
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Market Chart */}
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-white">Market Overview</h2>
            <select
              value={selectedCoin}
              onChange={(e) => setSelectedCoin(e.target.value)}
              className="bg-gray-700 text-white px-3 py-1 rounded border border-gray-600 focus:outline-none focus:border-blue-400"
            >
              {coins.map(coin => (
                <option key={coin} value={coin}>{coin}</option>
              ))}
            </select>
          </div>
          <MarketChart coin={selectedCoin} />
        </div>

        {/* Market Data */}
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h2 className="text-xl font-bold text-white mb-4">Market Prices</h2>
          <div className="space-y-4">
            {coins.map(coin => {
              const data = marketData[coin];
              if (!data) return null;
              
              return (
                <div key={coin} className="flex items-center justify-between p-3 bg-gray-700 rounded">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-sm font-bold">
                      {coin[0]}
                    </div>
                    <div>
                      <p className="font-semibold text-white">{coin}</p>
                      <p className="text-sm text-gray-400">{data.coin}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-white">
                      ${data.price?.toLocaleString('en-US', { 
                        minimumFractionDigits: 2, 
                        maximumFractionDigits: 2 
                      })}
                    </p>
                    <p className={`text-sm ${
                      data.change_24h >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {formatPercentage(data.change_24h)}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Current Positions */}
      {portfolio?.positions && portfolio.positions.length > 0 && (
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h2 className="text-xl font-bold text-white mb-4">Current Positions</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="pb-3 text-gray-400">Asset</th>
                  <th className="pb-3 text-gray-400">Side</th>
                  <th className="pb-3 text-gray-400">Size</th>
                  <th className="pb-3 text-gray-400">Entry Price</th>
                  <th className="pb-3 text-gray-400">Current Price</th>
                  <th className="pb-3 text-gray-400">PnL</th>
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
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;