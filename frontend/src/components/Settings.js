import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Settings as SettingsIcon, Key, Shield, AlertCircle, CheckCircle, Eye, EyeOff } from 'lucide-react';
import LoadingSpinner from './LoadingSpinner';

const Settings = () => {
  const [settings, setSettings] = useState(null);
  const [apiStatus, setApiStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [message, setMessage] = useState(null);
  const [showPrivateKey, setShowPrivateKey] = useState(false);
  
  const [formData, setFormData] = useState({
    wallet_address: '',
    api_key: '',
    api_secret: '',
    environment: 'mainnet'
  });

  useEffect(() => {
    fetchSettings();
    checkApiStatus();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/settings');
      if (response.data.success) {
        setSettings(response.data.data);
        setFormData({
          wallet_address: response.data.data.api_credentials?.wallet_address || '',
          api_key: response.data.data.api_credentials?.api_key || '',
          api_secret: response.data.data.api_credentials?.api_secret || '',
          environment: response.data.data.api_credentials?.environment || 'mainnet'
        });
      }
    } catch (error) {
      console.error('Error fetching settings:', error);
      setMessage({ type: 'error', text: 'Failed to fetch settings' });
    } finally {
      setLoading(false);
    }
  };

  const checkApiStatus = async () => {
    try {
      const response = await axios.get('/api/settings/api-status');
      if (response.data.success) {
        setApiStatus(response.data.data);
      }
    } catch (error) {
      console.error('Error checking API status:', error);
    }
  };

  const handleSaveSettings = async (e) => {
    e.preventDefault();
    
    try {
      setSaving(true);
      setMessage(null);

      const updatedSettings = {
        ...settings,
        api_credentials: {
          wallet_address: formData.wallet_address,
          api_key: formData.api_key,
          api_secret: formData.api_secret,
          environment: formData.environment,
          is_configured: Boolean(formData.wallet_address && formData.api_key && formData.api_secret)
        }
      };

      const response = await axios.put('/api/settings', updatedSettings);
      
      if (response.data.success) {
        setMessage({ type: 'success', text: 'Settings saved successfully!' });
        setSettings(response.data.data);
        checkApiStatus(); // Refresh API status
      } else {
        setMessage({ type: 'error', text: response.data.message || 'Failed to save settings' });
      }

    } catch (error) {
      console.error('Error saving settings:', error);
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Failed to save settings' 
      });
    } finally {
      setSaving(false);
    }
  };

  const handleTestConnection = async () => {
    try {
      setTesting(true);
      setMessage(null);

      // First save the settings if they've changed
      if (formData.wallet_address !== settings?.api_credentials?.wallet_address ||
          formData.api_secret !== settings?.api_credentials?.api_secret ||
          formData.environment !== settings?.api_credentials?.environment) {
        await handleSaveSettings({ preventDefault: () => {} });
        await new Promise(resolve => setTimeout(resolve, 1000)); // Wait for settings to be applied
      }

      const response = await axios.get('/api/settings/api-status');
      
      if (response.data.success) {
        setApiStatus(response.data.data);
        
        if (response.data.data.is_configured && response.data.data.test_result?.includes('successfully')) {
          setMessage({ type: 'success', text: 'API connection test successful!' });
        } else {
          setMessage({ 
            type: 'error', 
            text: response.data.data.test_result || 'API connection test failed' 
          });
        }
      }

    } catch (error) {
      console.error('Error testing connection:', error);
      setMessage({ type: 'error', text: 'Failed to test API connection' });
    } finally {
      setTesting(false);
    }
  };

  const getStatusIcon = () => {
    if (!apiStatus) return null;
    
    if (apiStatus.is_configured && apiStatus.test_result?.includes('successfully')) {
      return <CheckCircle className="w-5 h-5 text-green-400" />;
    } else if (apiStatus.is_configured) {
      return <AlertCircle className="w-5 h-5 text-red-400" />;
    } else {
      return <AlertCircle className="w-5 h-5 text-yellow-400" />;
    }
  };

  const getStatusText = () => {
    if (!apiStatus) return 'Checking...';
    
    if (apiStatus.is_configured && apiStatus.test_result?.includes('successfully')) {
      return 'Connected and working';
    } else if (apiStatus.is_configured) {
      return 'Configured but connection failed';
    } else {
      return 'Not configured';
    }
  };

  const getStatusColor = () => {
    if (!apiStatus) return 'text-gray-400';
    
    if (apiStatus.is_configured && apiStatus.test_result?.includes('successfully')) {
      return 'text-green-400';
    } else if (apiStatus.is_configured) {
      return 'text-red-400';
    } else {
      return 'text-yellow-400';
    }
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
      <div className="flex items-center space-x-3">
        <SettingsIcon className="w-8 h-8 text-blue-400" />
        <h1 className="text-3xl font-bold text-white">Settings</h1>
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* API Configuration */}
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center space-x-3 mb-4">
            <Key className="w-6 h-6 text-blue-400" />
            <h2 className="text-xl font-bold text-white">API Configuration</h2>
          </div>

          {/* API Status */}
          <div className="mb-6 p-4 bg-gray-700 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400">Connection Status:</span>
              <div className="flex items-center space-x-2">
                {getStatusIcon()}
                <span className={`font-medium ${getStatusColor()}`}>
                  {getStatusText()}
                </span>
              </div>
            </div>
            
            {apiStatus && (
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Environment:</span>
                  <span className="text-white capitalize">{apiStatus.environment}</span>
                </div>
                {apiStatus.test_result && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Test Result:</span>
                    <span className={`${apiStatus.test_result.includes('successfully') ? 'text-green-400' : 'text-red-400'}`}>
                      {apiStatus.test_result}
                    </span>
                  </div>
                )}
              </div>
            )}
          </div>

          <form onSubmit={handleSaveSettings} className="space-y-4">
            {/* Environment Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Environment
              </label>
              <select
                value={formData.environment}
                onChange={(e) => setFormData(prev => ({ ...prev, environment: e.target.value }))}
                className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-400"
              >
                <option value="mainnet">Mainnet (Live Trading)</option>
                <option value="testnet">Testnet (Paper Trading)</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">
                {formData.environment === 'testnet' 
                  ? 'Use testnet for safe testing with fake funds'
                  : 'Use mainnet for live trading with real funds'
                }
              </p>
            </div>

            {/* Main Wallet Address */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Main Wallet Address
              </label>
              <input
                type="text"
                value={formData.wallet_address}
                onChange={(e) => setFormData(prev => ({ ...prev, wallet_address: e.target.value }))}
                className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:outline-none focus:border-blue-400"
                placeholder="0x1234567890abcdef1234567890abcdef12345678"
              />
              <p className="text-xs text-gray-500 mt-1">
                Your main wallet address from Hyperliquid (master account address).
              </p>
            </div>

            {/* API Secret Key */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Hyperliquid API Secret Key
              </label>
              <div className="relative">
                <input
                  type={showPrivateKey ? 'text' : 'password'}
                  value={formData.api_secret}
                  onChange={(e) => setFormData(prev => ({ ...prev, api_secret: e.target.value }))}
                  className="w-full bg-gray-700 text-white px-3 py-2 pr-10 rounded border border-gray-600 focus:outline-none focus:border-blue-400"
                  placeholder="Enter your Hyperliquid API secret key"
                />
                <button
                  type="button"
                  onClick={() => setShowPrivateKey(!showPrivateKey)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
                >
                  {showPrivateKey ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                The API secret key generated from your Hyperliquid API wallet.
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-3 pt-4">
              <button
                type="submit"
                disabled={saving}
                className="flex-1 py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded text-white transition-colors"
              >
                {saving ? <LoadingSpinner size="small" /> : 'Save Settings'}
              </button>
              
              <button
                type="button"
                onClick={handleTestConnection}
                disabled={testing || !formData.wallet_address || !formData.api_secret}
                className="py-2 px-4 bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed rounded text-white transition-colors"
              >
                {testing ? <LoadingSpinner size="small" /> : 'Test Connection'}
              </button>
            </div>
          </form>
        </div>

        {/* Security Information */}
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center space-x-3 mb-4">
            <Shield className="w-6 h-6 text-green-400" />
            <h2 className="text-xl font-bold text-white">Security Information</h2>
          </div>

          <div className="space-y-4">
            <div className="p-4 bg-blue-900 bg-opacity-30 border border-blue-700 rounded-lg">
              <h3 className="font-semibold text-blue-300 mb-2">How to get your Hyperliquid API credentials:</h3>
              <ol className="text-sm text-blue-200 space-y-1 list-decimal list-inside">
                <li>Go to <a href="https://app.hyperliquid.xyz/API" target="_blank" rel="noopener noreferrer" className="underline">Hyperliquid API Management</a></li>
                <li>Copy your <strong>main wallet address</strong> from the top-right dropdown</li>
                <li>Enter a descriptive name for your API wallet</li>
                <li>Click "Generate" to create the API wallet</li>
                <li>Click "Authorize API Wallet" to reveal the API secret key</li>
                <li>Copy both the <strong>main wallet address</strong> and <strong>API secret key</strong></li>
                <li>Paste them into the fields above</li>
              </ol>
            </div>

            <div className="p-4 bg-green-900 bg-opacity-30 border border-green-700 rounded-lg">
              <h3 className="font-semibold text-green-300 mb-2">Security Features:</h3>
              <ul className="text-sm text-green-200 space-y-1">
                <li>• Private keys are encrypted in storage</li>
                <li>• All API calls use secure HTTPS</li>
                <li>• No keys are logged or transmitted unnecessarily</li>
                <li>• Testnet environment for safe testing</li>
              </ul>
            </div>

            <div className="p-4 bg-yellow-900 bg-opacity-30 border border-yellow-700 rounded-lg">
              <h3 className="font-semibold text-yellow-300 mb-2">Important Notes:</h3>
              <ul className="text-sm text-yellow-200 space-y-1">
                <li>• <strong>Main Wallet Address:</strong> Your master account address from Hyperliquid</li>
                <li>• <strong>API Secret Key:</strong> The secret key from your generated API wallet</li>
                <li>• Choose mainnet for live trading or testnet for paper trading</li>
                <li>• Never share your API secret key with anyone</li>
                <li>• Monitor your account regularly for security</li>
              </ul>
            </div>

            <div className="p-4 bg-red-900 bg-opacity-30 border border-red-700 rounded-lg">
              <h3 className="font-semibold text-red-300 mb-2">Fallback Mode:</h3>
              <p className="text-sm text-red-200">
                If no API credentials are provided, the application will run in demo mode with mock data. 
                This allows you to explore the interface without real trading capabilities.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;