// © 2025 Deepak Raghunath Raut — All rights reserved. MIT Licensed.
import React from 'react';
import { Shield, LayoutDashboard, Activity, Bell, LogOut } from 'lucide-react';

const Header = ({ walletConnected, selectedAccount, onDisconnect, activeView, setActiveView }) => {
  const formatAddress = (address) => {
    if (!address) return '';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  return (
    <header className="bg-slate-900/80 backdrop-blur-lg border-b border-purple-500/20 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8 text-purple-400" />
            <div>
              <h1 className="text-2xl font-bold text-white" data-testid="app-title">SAFDO</h1>
              <p className="text-xs text-purple-300">Crypto Shield</p>
            </div>
          </div>

          {walletConnected && (
            <nav className="flex items-center gap-4">
              <button
                onClick={() => setActiveView('dashboard')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${
                  activeView === 'dashboard'
                    ? 'bg-purple-600 text-white'
                    : 'text-white/70 hover:text-white hover:bg-white/10'
                }`}
                data-testid="nav-dashboard"
              >
                <LayoutDashboard className="w-4 h-4" />
                Dashboard
              </button>
              <button
                onClick={() => setActiveView('transactions')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${
                  activeView === 'transactions'
                    ? 'bg-purple-600 text-white'
                    : 'text-white/70 hover:text-white hover:bg-white/10'
                }`}
                data-testid="nav-transactions"
              >
                <Activity className="w-4 h-4" />
                Transactions
              </button>
              <button
                onClick={() => setActiveView('notifications')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${
                  activeView === 'notifications'
                    ? 'bg-purple-600 text-white'
                    : 'text-white/70 hover:text-white hover:bg-white/10'
                }`}
                data-testid="nav-notifications"
              >
                <Bell className="w-4 h-4" />
                Notifications
              </button>
            </nav>
          )}

          {walletConnected && selectedAccount && (
            <div className="flex items-center gap-3">
              <div className="text-right">
                <p className="text-xs text-white/60">Connected</p>
                <p className="text-sm text-white font-mono" data-testid="connected-address">
                  {formatAddress(selectedAccount.address)}
                </p>
              </div>
              <button
                onClick={onDisconnect}
                className="p-2 rounded-lg bg-red-500/20 text-red-300 hover:bg-red-500/30 transition"
                data-testid="disconnect-wallet-btn"
                title="Disconnect Wallet"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
