import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Brain, Plus, Play, Pause, Stop, Edit, Trash2, TrendingUp, AlertCircle } from 'lucide-react';
import LoadingSpinner from './LoadingSpinner';

const Strategies = () => {
  const [strategies, setStrategies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingStrategy, setEditingStrategy] = useState(null);
  const [message, setMessage] = useState(null);
  
  const [strategyForm, setStrategyForm] = useState({
    name: '',
    description: '',
    coin: 'BTC',
    config: {
      entry_conditions: {},
      exit_conditions: {},
      risk_management: { max_loss: 100, max_position_size: 1 },
      position_sizing: { size_type: 'fixed', amount: 0.1 }
    }
  });

  const coins = ['BTC', 'ETH', 'SOL', 'AVAX', 'MATIC', 'LINK'];

  useEffect(() => {
    fetchStrategies();
  }, []);

  const fetchStrategies = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/strategies');
      if (response.data.success) {
        setStrategies(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching strategies:', error);
      setMessage({ type: 'error', text: 'Failed to fetch strategies' });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateStrategy = async (e) => {
    e.preventDefault();
    
    if (!strategyForm.name.trim()) {
      setMessage({ type: 'error', text: 'Strategy name is required' });
      return;
    }

    try {
      const response = await axios.post('/api/strategies', {
        ...strategyForm,
        status: 'active',
        performance: {
          total_trades: 0,
          win_rate: 0,
          total_pnl: 0,
          max_drawdown: 0
        }
      });

      if (response.data.success) {
        setMessage({ type: 'success', text: 'Strategy created successfully!' });
        setShowCreateModal(false);
        resetForm();
        fetchStrategies();
      }
    } catch (error) {
      console.error('Error creating strategy:', error);
      setMessage({ type: 'error', text: 'Failed to create strategy' });
    }
  };

  const handleUpdateStrategy = async (e) => {
    e.preventDefault();
    
    if (!editingStrategy) return;

    try {
      const response = await axios.put(`/api/strategies/${editingStrategy.id}`, strategyForm);

      if (response.data.success) {
        setMessage({ type: 'success', text: 'Strategy updated successfully!' });
        setEditingStrategy(null);
        resetForm();
        fetchStrategies();
      }
    } catch (error) {
      console.error('Error updating strategy:', error);
      setMessage({ type: 'error', text: 'Failed to update strategy' });
    }
  };

  const handleDeleteStrategy = async (strategyId) => {
    if (!window.confirm('Are you sure you want to delete this strategy?')) {
      return;
    }

    try {
      const response = await axios.delete(`/api/strategies/${strategyId}`);
      
      if (response.data.success) {
        setMessage({ type: 'success', text: 'Strategy deleted successfully!' });
        fetchStrategies();
      }
    } catch (error) {
      console.error('Error deleting strategy:', error);
      setMessage({ type: 'error', text: 'Failed to delete strategy' });
    }
  };

  const handleStatusChange = async (strategyId, newStatus) => {
    try {
      const strategy = strategies.find(s => s.id === strategyId);
      const response = await axios.put(`/api/strategies/${strategyId}`, {
        ...strategy,
        status: newStatus
      });

      if (response.data.success) {
        setMessage({ type: 'success', text: `Strategy ${newStatus} successfully!` });
        fetchStrategies();
      }
    } catch (error) {
      console.error('Error updating strategy status:', error);
      setMessage({ type: 'error', text: 'Failed to update strategy status' });
    }
  };

  const resetForm = () => {
    setStrategyForm({
      name: '',
      description: '',
      coin: 'BTC',
      config: {
        entry_conditions: {},
        exit_conditions: {},
        risk_management: { max_loss: 100, max_position_size: 1 },
        position_sizing: { size_type: 'fixed', amount: 0.1 }
      }
    });
  };

  const openEditModal = (strategy) => {
    setEditingStrategy(strategy);
    setStrategyForm({
      name: strategy.name,
      description: strategy.description || '',
      coin: strategy.coin,
      config: strategy.config
    });
    setShowCreateModal(true);
  };

  const closeModal = () => {
    setShowCreateModal(false);
    setEditingStrategy(null);
    resetForm();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-900 text-green-300';
      case 'paused':
        return 'bg-yellow-900 text-yellow-300';
      case 'stopped':
        return 'bg-red-900 text-red-300';
      default:
        return 'bg-gray-900 text-gray-300';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <Play size={16} />;
      case 'paused':
        return <Pause size={16} />;
      case 'stopped':
        return <Stop size={16} />;
      default:
        return null;
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">Trading Strategies</h1>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
        >
          <Plus size={20} />
          <span>Create Strategy</span>
        </button>
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
          <button 
            onClick={() => setMessage(null)}
            className="ml-auto text-current hover:opacity-70"
          >
            ×
          </button>
        </div>
      )}

      {/* Strategies Grid */}
      {loading ? (
        <div className="flex justify-center py-12">
          <LoadingSpinner size="large" />
        </div>
      ) : strategies.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {strategies.map((strategy) => (
            <div key={strategy.id} className="bg-gray-800 p-6 rounded-lg border border-gray-700">
              {/* Strategy Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-white mb-1">{strategy.name}</h3>
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-sm text-gray-400">{strategy.coin}</span>
                    <span className={`px-2 py-1 rounded text-xs font-medium flex items-center space-x-1 ${getStatusColor(strategy.status)}`}>
                      {getStatusIcon(strategy.status)}
                      <span>{strategy.status.toUpperCase()}</span>
                    </span>
                  </div>
                  {strategy.description && (
                    <p className="text-sm text-gray-400 mb-3">{strategy.description}</p>
                  )}
                </div>
              </div>

              {/* Strategy Performance */}
              <div className="mb-4 p-3 bg-gray-700 rounded">
                <h4 className="text-sm font-medium text-gray-300 mb-2">Performance</h4>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-gray-400">Trades:</span>
                    <span className="text-white ml-1">{strategy.performance?.total_trades || 0}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Win Rate:</span>
                    <span className="text-white ml-1">{strategy.performance?.win_rate || 0}%</span>
                  </div>
                  <div>
                    <span className="text-gray-400">PnL:</span>
                    <span className={`ml-1 ${(strategy.performance?.total_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      ${strategy.performance?.total_pnl || 0}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">Drawdown:</span>
                    <span className="text-red-400 ml-1">{strategy.performance?.max_drawdown || 0}%</span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-between">
                <div className="flex space-x-1">
                  {strategy.status !== 'active' && (
                    <button
                      onClick={() => handleStatusChange(strategy.id, 'active')}
                      className="p-2 bg-green-600 hover:bg-green-700 rounded text-white transition-colors"
                      title="Start Strategy"
                    >
                      <Play size={16} />
                    </button>
                  )}
                  {strategy.status === 'active' && (
                    <button
                      onClick={() => handleStatusChange(strategy.id, 'paused')}
                      className="p-2 bg-yellow-600 hover:bg-yellow-700 rounded text-white transition-colors"
                      title="Pause Strategy"
                    >
                      <Pause size={16} />
                    </button>
                  )}
                  {strategy.status !== 'stopped' && (
                    <button
                      onClick={() => handleStatusChange(strategy.id, 'stopped')}
                      className="p-2 bg-red-600 hover:bg-red-700 rounded text-white transition-colors"
                      title="Stop Strategy"
                    >
                      <Stop size={16} />
                    </button>
                  )}
                </div>
                
                <div className="flex space-x-1">
                  <button
                    onClick={() => openEditModal(strategy)}
                    className="p-2 bg-blue-600 hover:bg-blue-700 rounded text-white transition-colors"
                    title="Edit Strategy"
                  >
                    <Edit size={16} />
                  </button>
                  <button
                    onClick={() => handleDeleteStrategy(strategy.id)}
                    className="p-2 bg-red-600 hover:bg-red-700 rounded text-white transition-colors"
                    title="Delete Strategy"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Brain className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400 text-lg">No strategies created yet</p>
          <p className="text-gray-500 text-sm mb-6">Create your first trading strategy to get started</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg text-white transition-colors"
          >
            Create Your First Strategy
          </button>
        </div>
      )}

      {/* Create/Edit Strategy Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 p-6 rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold text-white mb-4">
              {editingStrategy ? 'Edit Strategy' : 'Create New Strategy'}
            </h2>
            
            <form onSubmit={editingStrategy ? handleUpdateStrategy : handleCreateStrategy} className="space-y-4">
              {/* Basic Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    Strategy Name *
                  </label>
                  <input
                    type="text"
                    value={strategyForm.name}
                    onChange={(e) => setStrategyForm(prev => ({ ...prev, name: e.target.value }))}
                    className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-400"
                    placeholder="Enter strategy name"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    Asset
                  </label>
                  <select
                    value={strategyForm.coin}
                    onChange={(e) => setStrategyForm(prev => ({ ...prev, coin: e.target.value }))}
                    className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-400"
                  >
                    {coins.map(coin => (
                      <option key={coin} value={coin}>{coin}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Description
                </label>
                <textarea
                  value={strategyForm.description}
                  onChange={(e) => setStrategyForm(prev => ({ ...prev, description: e.target.value }))}
                  className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-400"
                  rows="3"
                  placeholder="Describe your trading strategy"
                />
              </div>

              {/* Risk Management */}
              <div className="border-t border-gray-700 pt-4">
                <h3 className="text-lg font-semibold text-white mb-3">Risk Management</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">
                      Max Loss ($)
                    </label>
                    <input
                      type="number"
                      value={strategyForm.config.risk_management.max_loss}
                      onChange={(e) => setStrategyForm(prev => ({
                        ...prev,
                        config: {
                          ...prev.config,
                          risk_management: {
                            ...prev.config.risk_management,
                            max_loss: parseFloat(e.target.value) || 0
                          }
                        }
                      }))}
                      className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-400"
                      min="0"
                      step="0.01"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">
                      Max Position Size
                    </label>
                    <input
                      type="number"
                      value={strategyForm.config.risk_management.max_position_size}
                      onChange={(e) => setStrategyForm(prev => ({
                        ...prev,
                        config: {
                          ...prev.config,
                          risk_management: {
                            ...prev.config.risk_management,
                            max_position_size: parseFloat(e.target.value) || 0
                          }
                        }
                      }))}
                      className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-400"
                      min="0"
                      step="0.001"
                    />
                  </div>
                </div>
              </div>

              {/* Position Sizing */}
              <div className="border-t border-gray-700 pt-4">
                <h3 className="text-lg font-semibold text-white mb-3">Position Sizing</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">
                      Size Type
                    </label>
                    <select
                      value={strategyForm.config.position_sizing.size_type}
                      onChange={(e) => setStrategyForm(prev => ({
                        ...prev,
                        config: {
                          ...prev.config,
                          position_sizing: {
                            ...prev.config.position_sizing,
                            size_type: e.target.value
                          }
                        }
                      }))}
                      className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-400"
                    >
                      <option value="fixed">Fixed</option>
                      <option value="percentage">Percentage</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">
                      Amount
                    </label>
                    <input
                      type="number"
                      value={strategyForm.config.position_sizing.amount}
                      onChange={(e) => setStrategyForm(prev => ({
                        ...prev,
                        config: {
                          ...prev.config,
                          position_sizing: {
                            ...prev.config.position_sizing,
                            amount: parseFloat(e.target.value) || 0
                          }
                        }
                      }))}
                      className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-400"
                      min="0"
                      step="0.001"
                    />
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex justify-end space-x-4 pt-4 border-t border-gray-700">
                <button
                  type="button"
                  onClick={closeModal}
                  className="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-white transition-colors"
                >
                  {editingStrategy ? 'Update Strategy' : 'Create Strategy'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Strategies;