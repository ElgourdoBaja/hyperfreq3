import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, TrendingUp, TrendingDown, Filter } from 'lucide-react';
import LoadingSpinner from './LoadingSpinner';

const MarketList = () => {
  const [coins, setCoins] = useState([]);
  const [marketData, setMarketData] = useState({});
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');
  const [leverageFilter, setLeverageFilter] = useState('all');

  useEffect(() => {
    fetchCoinsAndMarketData();
    const interval = setInterval(fetchMarketData, 30000); // Update prices every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchCoinsAndMarketData = async () => {
    try {
      setLoading(true);
      
      // Get all available coins
      const coinsResponse = await axios.get('/api/coins');
      if (coinsResponse.data.success) {
        const allCoins = coinsResponse.data.data;
        setCoins(allCoins);
        
        // Fetch market data for top 50 coins
        await fetchMarketDataForCoins(allCoins.slice(0, 50));
      }
    } catch (error) {
      console.error('Error fetching coins data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMarketData = async () => {
    if (coins.length > 0) {
      await fetchMarketDataForCoins(coins.slice(0, 50));
    }
  };

  const fetchMarketDataForCoins = async (coinList) => {
    try {
      const marketPromises = coinList.map(async (coin) => {
        try {
          const response = await axios.get(`/api/market/${coin.symbol}`);
          return {
            symbol: coin.symbol,
            data: response.data.success ? response.data.data : null
          };
        } catch (error) {
          return { symbol: coin.symbol, data: null };
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
      console.error('Error fetching market data:', error);
    }
  };

  const formatPrice = (price) => {
    if (!price) return '$0.00';
    
    if (price >= 1000) {
      return `$${price.toLocaleString('en-US', { 
        minimumFractionDigits: 2, 
        maximumFractionDigits: 2 
      })}`;
    } else if (price >= 1) {
      return `$${price.toFixed(4)}`;
    } else {
      return `$${price.toFixed(6)}`;
    }
  };

  const formatVolume = (volume) => {
    if (!volume) return '$0';
    
    if (volume >= 1e9) {
      return `$${(volume / 1e9).toFixed(2)}B`;
    } else if (volume >= 1e6) {
      return `$${(volume / 1e6).toFixed(2)}M`;
    } else if (volume >= 1e3) {
      return `$${(volume / 1e3).toFixed(2)}K`;
    }
    return `$${volume.toFixed(0)}`;
  };

  const filteredAndSortedCoins = coins
    .filter(coin => {
      const matchesSearch = coin.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           coin.name.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesLeverage = leverageFilter === 'all' || 
        (leverageFilter === 'high' && coin.maxLeverage >= 20) ||
        (leverageFilter === 'medium' && coin.maxLeverage >= 10 && coin.maxLeverage < 20) ||
        (leverageFilter === 'low' && coin.maxLeverage < 10);
      
      return matchesSearch && matchesLeverage;
    })
    .sort((a, b) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case 'name':
          aValue = a.symbol;
          bValue = b.symbol;
          break;
        case 'price':
          aValue = marketData[a.symbol]?.price || 0;
          bValue = marketData[b.symbol]?.price || 0;
          break;
        case 'change':
          aValue = marketData[a.symbol]?.change_24h || 0;
          bValue = marketData[b.symbol]?.change_24h || 0;
          break;
        case 'volume':
          aValue = marketData[a.symbol]?.volume_24h || 0;
          bValue = marketData[b.symbol]?.volume_24h || 0;
          break;
        case 'leverage':
          aValue = a.maxLeverage;
          bValue = b.maxLeverage;
          break;
        default:
          aValue = a.symbol;
          bValue = b.symbol;
      }
      
      if (typeof aValue === 'string') {
        return sortOrder === 'asc' ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
      }
      
      return sortOrder === 'asc' ? aValue - bValue : bValue - aValue;
    });

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const getSortIcon = (field) => {
    if (sortBy !== field) return null;
    return sortOrder === 'asc' ? '↑' : '↓';
  };

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
        <h1 className="text-3xl font-bold text-white">Hyperliquid Perpetuals Market</h1>
        <div className="text-sm text-gray-400">
          {coins.length} Trading Pairs Available
        </div>
      </div>

      {/* Top 100 Hyperliquid Perpetuals List */}
      <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-4">
        <h2 className="text-lg font-bold text-blue-300 mb-2">📊 Top 100 Hyperliquid Perpetual Futures</h2>
        <p className="text-blue-200 text-sm">
          Complete list of the top 100 perpetual futures contracts available on Hyperliquid with real-time pricing, 
          24h changes, trading volumes, and maximum leverage for each pair.
        </p>
      </div>

      {/* Filters and Search */}
      <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search pairs (BTC, ETH, SOL, etc.)..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-gray-700 text-white pl-10 pr-4 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-400"
            />
          </div>

          {/* Leverage Filter */}
          <div className="flex items-center space-x-2">
            <Filter className="text-gray-400 w-4 h-4" />
            <select
              value={leverageFilter}
              onChange={(e) => setLeverageFilter(e.target.value)}
              className="bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-400"
            >
              <option value="all">All Leverage</option>
              <option value="high">High (≥20x)</option>
              <option value="medium">Medium (10-19x)</option>
              <option value="low">Low (&lt;10x)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Market Table */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-900 border-b border-gray-700">
              <tr>
                <th className="text-left p-4 text-gray-400 font-medium">Rank</th>
                <th 
                  className="text-left p-4 text-gray-400 font-medium cursor-pointer hover:text-white"
                  onClick={() => handleSort('name')}
                >
                  Perpetual Contract {getSortIcon('name')}
                </th>
                <th 
                  className="text-right p-4 text-gray-400 font-medium cursor-pointer hover:text-white"
                  onClick={() => handleSort('price')}
                >
                  Mark Price {getSortIcon('price')}
                </th>
                <th 
                  className="text-right p-4 text-gray-400 font-medium cursor-pointer hover:text-white"
                  onClick={() => handleSort('change')}
                >
                  24h Change {getSortIcon('change')}
                </th>
                <th 
                  className="text-right p-4 text-gray-400 font-medium cursor-pointer hover:text-white"
                  onClick={() => handleSort('volume')}
                >
                  24h Volume {getSortIcon('volume')}
                </th>
                <th 
                  className="text-right p-4 text-gray-400 font-medium cursor-pointer hover:text-white"
                  onClick={() => handleSort('leverage')}
                >
                  Max Leverage {getSortIcon('leverage')}
                </th>
                <th className="text-center p-4 text-gray-400 font-medium">Long/Short</th>
              </tr>
            </thead>
            <tbody>
              {filteredAndSortedCoins.slice(0, 100).map((coin, index) => {
                const market = marketData[coin.symbol];
                const hasPrice = market && market.price;
                const change24h = market?.change_24h || 0;
                
                return (
                  <tr key={coin.symbol} className="border-b border-gray-700/50 hover:bg-gray-700/30">
                    <td className="p-4 text-gray-400">
                      {`#${index + 1}`}
                    </td>
                    
                    <td className="p-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-sm font-bold">
                          {coin.symbol[0]}
                        </div>
                        <div>
                          <div className="font-semibold text-white">{coin.symbol}-PERP</div>
                          <div className="text-sm text-gray-400">{coin.name}</div>
                        </div>
                      </div>
                    </td>
                    
                    <td className="p-4 text-right">
                      {hasPrice ? (
                        <div className="text-white font-semibold">
                          {formatPrice(market.price)}
                        </div>
                      ) : (
                        <div className="text-gray-500">Loading...</div>
                      )}
                    </td>
                    
                    <td className="p-4 text-right">
                      {hasPrice ? (
                        <div className={`flex items-center justify-end space-x-1 ${
                          change24h >= 0 ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {change24h >= 0 ? 
                            <TrendingUp size={14} /> : 
                            <TrendingDown size={14} />
                          }
                          <span className="font-semibold">
                            {change24h >= 0 ? '+' : ''}{change24h.toFixed(2)}%
                          </span>
                        </div>
                      ) : (
                        <div className="text-gray-500">-</div>
                      )}
                    </td>
                    
                    <td className="p-4 text-right">
                      {hasPrice ? (
                        <div className="text-white">
                          {formatVolume(market.volume_24h)}
                        </div>
                      ) : (
                        <div className="text-gray-500">-</div>
                      )}
                    </td>
                    
                    <td className="p-4 text-right">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        coin.maxLeverage >= 20 ? 'bg-red-900 text-red-300' :
                        coin.maxLeverage >= 10 ? 'bg-yellow-900 text-yellow-300' :
                        'bg-green-900 text-green-300'
                      }`}>
                        {coin.maxLeverage}x
                      </span>
                    </td>
                    
                    <td className="p-4 text-center">
                      <div className="flex items-center justify-center space-x-2">
                        <button
                          className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-xs rounded transition-colors"
                        >
                          LONG
                        </button>
                        <button
                          className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-xs rounded transition-colors"
                        >
                          SHORT
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Market Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <div className="text-sm text-gray-400">Total Perpetuals</div>
          <div className="text-2xl font-bold text-white">{coins.length}</div>
          <div className="text-xs text-gray-500">Available on Hyperliquid</div>
        </div>
        
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <div className="text-sm text-gray-400">High Leverage (≥20x)</div>
          <div className="text-2xl font-bold text-red-400">
            {coins.filter(c => c.maxLeverage >= 20).length}
          </div>
          <div className="text-xs text-gray-500">Max risk contracts</div>
        </div>
        
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <div className="text-sm text-gray-400">Medium Leverage (10-19x)</div>
          <div className="text-2xl font-bold text-yellow-400">
            {coins.filter(c => c.maxLeverage >= 10 && c.maxLeverage < 20).length}
          </div>
          <div className="text-xs text-gray-500">Moderate risk contracts</div>
        </div>
        
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <div className="text-sm text-gray-400">Low Leverage (&lt;10x)</div>
          <div className="text-2xl font-bold text-green-400">
            {coins.filter(c => c.maxLeverage < 10).length}
          </div>
          <div className="text-xs text-gray-500">Lower risk contracts</div>
        </div>
      </div>
    </div>
  );
};

export default MarketList;