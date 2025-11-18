// © 2025 Deepak Raghunath Raut — All rights reserved. MIT Licensed.
import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import axios from 'axios';
import '@/App.css';

// Import components
import Header from '@/components/Header';
import Dashboard from '@/components/Dashboard';
import TransactionFeed from '@/components/TransactionFeed';
import NotificationSettings from '@/components/NotificationSettings';
import WalletConnect from '@/components/WalletConnect';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [walletConnected, setWalletConnected] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [activeView, setActiveView] = useState('dashboard');

  useEffect(() => {
    // Check health on mount
    const checkHealth = async () => {
      try {
        const response = await axios.get(`${API}/health`);
        console.log('Backend health:', response.data);
      } catch (error) {
        console.error('Backend health check failed:', error);
      }
    };
    checkHealth();
  }, []);

  const handleWalletConnected = (account) => {
    setWalletConnected(true);
    setSelectedAccount(account);
  };

  const handleWalletDisconnected = () => {
    setWalletConnected(false);
    setSelectedAccount(null);
  };

  return (
    <div className="App min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <BrowserRouter>
        <Header
          walletConnected={walletConnected}
          selectedAccount={selectedAccount}
          onDisconnect={handleWalletDisconnected}
          activeView={activeView}
          setActiveView={setActiveView}
        />
        
        <main className="container mx-auto px-4 py-8">
          {!walletConnected ? (
            <WalletConnect onConnect={handleWalletConnected} />
          ) : (
            <>
              {activeView === 'dashboard' && (
                <Dashboard account={selectedAccount} />
              )}
              {activeView === 'transactions' && (
                <TransactionFeed account={selectedAccount} />
              )}
              {activeView === 'notifications' && (
                <NotificationSettings account={selectedAccount} />
              )}
            </>
          )}
        </main>

        <footer className="text-center py-8 text-white/60 text-sm">
          <p>© 2025 Deepak Raghunath Raut — SAFDO Crypto Shield — MIT Licensed</p>
          <p className="mt-2">Securing the Polkadot Ecosystem</p>
        </footer>
      </BrowserRouter>
    </div>
  );
}

export default App;
