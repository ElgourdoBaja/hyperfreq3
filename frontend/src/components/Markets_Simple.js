import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, TrendingUp, TrendingDown } from 'lucide-react';
import LoadingSpinner from './LoadingSpinner';

const Markets = () => {
  const [coins, setCoins] = useState([]);
  const [marketData, setMarketData] = useState({});
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Get all available coins
      const coinsResponse = await axios.get('/api/coins');
      if (coinsResponse.data.success) {
        setCoins(coinsResponse.data.data);
      }

      // Fetch market data only for top 5 coins to test
      const topCoins = ['BTC', 'ETH', 'SOL', 'AVAX', 'MATIC'];
      const marketPromises = topCoins.map(async (coin) => {
        try {
          const response = await axios.get(`/api/market/${coin}`);
          return {
            symbol: coin,
            data: response.data.success ? response.data.data : null
          };
        } catch (error) {
          console.warn(`Failed to fetch ${coin}:`, error);
          return { symbol: coin, data: null };
        }
      });

      const results = await Promise.all(marketPromises);
      const marketDataMap = {};
      
      results.forEach(result => {
        if (result.data) {
          marketDataMap[result.symbol] = result.data;
        }
      });
      
      setMarketData(marketDataMap);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price) => {
    if (!price) return '$0.00';
    return `$${price.toLocaleString('en-US', { 
      minimumFractionDigits: 2, 
      maximumFractionDigits: 2 
    })}`;
  };

  const formatChange = (change) => {
    if (!change) return '0.00%';
    const sign = change >= 0 ? '+' : '';
    return `${sign}${change.toFixed(2)}%`;
  };

  const filteredCoins = coins.filter(coin =>
    coin.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
    coin.name.toLowerCase().includes(searchTerm.toLowerCase())
  ).slice(0, 50); // Limit to 50 for performance

  if (loading) {
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
        <h1 className="text-3xl font-bold text-white">Markets</h1>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search markets..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 pr-4 py-2 bg-gray-700 text-white rounded-lg border border-gray-600 focus:outline-none focus:border-blue-400"
          />
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {Object.entries(marketData).slice(0, 4).map(([symbol, data]) => (
          <div key={symbol} className="bg-gray-800 p-4 rounded-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">{symbol}</p>
                <p className="text-lg font-bold text-white">{formatPrice(data.price)}</p>
              </div>
              <div className={`flex items-center space-x-1 ${
                data.change_24h >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {data.change_24h >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                <span className="text-sm font-medium">{formatChange(data.change_24h)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Markets Table */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="p-4 border-b border-gray-700">
          <h2 className="text-xl font-bold text-white">All Markets ({filteredCoins.length})</h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Market
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  24h Change
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Max Leverage
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {filteredCoins.map((coin) => {
                const data = marketData[coin.symbol];
                return (
                  <tr key={coin.symbol} className="hover:bg-gray-700/50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-sm font-bold mr-3">
                          {coin.symbol[0]}
                        </div>
                        <div>
                          <div className="text-sm font-medium text-white">{coin.symbol}</div>
                          <div className="text-sm text-gray-400">{coin.name}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-white">
                        {data ? formatPrice(data.price) : 'Loading...'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className={`flex items-center space-x-1 ${
                        data && data.change_24h >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {data && (data.change_24h >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />)}
                        <span className="text-sm font-medium">
                          {data ? formatChange(data.change_24h) : '--'}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-white">{coin.maxLeverage}x</div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Markets;