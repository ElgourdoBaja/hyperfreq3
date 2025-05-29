import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  BarChart3, 
  TrendingUp, 
  Wallet, 
  Brain, 
  Settings as SettingsIcon,
  PieChart
} from 'lucide-react';

const Navigation = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: PieChart, path: '/dashboard' },
    { id: 'trading', label: 'Trading', icon: TrendingUp, path: '/trading' },
    { id: 'portfolio', label: 'Portfolio', icon: Wallet, path: '/portfolio' },
    { id: 'strategies', label: 'Strategies', icon: Brain, path: '/strategies' },
    { id: 'settings', label: 'Settings', icon: SettingsIcon, path: '/settings' },
  ];

  return (
    <nav className="w-64 bg-gray-800 border-r border-gray-700 h-full">
      <div className="p-6">
        <ul className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <li key={item.id}>
                <button
                  onClick={() => navigate(item.path)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                  }`}
                >
                  <Icon size={20} />
                  <span className="font-medium">{item.label}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </div>
    </nav>
  );
};

export default Navigation;