// © 2025 Deepak Raghunath Raut — All rights reserved. MIT Licensed.
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TrendingUp, Shield, Activity, Loader2, AlertTriangle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = ({ account }) => {
  const [balances, setBalances] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedChains, setSelectedChains] = useState(['polkadot', 'kusama', 'westend']);

  useEffect(() => {
    if (account && account.address) {
      fetchBalances();
    }
  }, [account, selectedChains]);

  const fetchBalances = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API}/chain-balance`, {
        address: account.address,
        chains: selectedChains
      });
      
      setBalances(response.data.balances || []);
    } catch (err) {
      console.error('Balance fetch error:', err);
      setError('Failed to fetch balances. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatBalance = (balance, decimals = 10) => {
    const value = Number(balance) / Math.pow(10, decimals);
    return value.toFixed(4);
  };

  const getChainSymbol = (chain) => {
    const symbols = {
      polkadot: 'DOT',
      kusama: 'KSM',
      westend: 'WND'
    };
    return symbols[chain] || 'TOKEN';
  };

  const getTotalValue = () => {
    return balances.reduce((sum, balance) => {
      return sum + (Number(balance.free) || 0);
    }, 0);
  };

  const toggleChain = (chain) => {
    setSelectedChains(prev => 
      prev.includes(chain)
        ? prev.filter(c => c !== chain)
        : [...prev, chain]
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2" data-testid="dashboard-title">Multi-Chain Dashboard</h2>
          <p className="text-white/60">View your balances across Polkadot ecosystem</p>
        </div>
        <button
          onClick={fetchBalances}
          disabled={loading}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-500 disabled:bg-gray-600 text-white rounded-lg transition flex items-center gap-2"
          data-testid="refresh-balances-btn"
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Activity className="w-4 h-4" />
          )}
          Refresh
        </button>
      </div>

      {/* Chain Selector */}
      <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-purple-500/20 p-4">
        <p className="text-white/80 font-semibold mb-3">Select Chains:</p>
        <div className="flex gap-3 flex-wrap">
          {['polkadot', 'kusama', 'westend'].map(chain => (
            <button
              key={chain}
              onClick={() => toggleChain(chain)}
              className={`px-4 py-2 rounded-lg font-semibold transition ${
                selectedChains.includes(chain)
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-700/50 text-white/60 hover:bg-slate-700'
              }`}
              data-testid={`chain-toggle-${chain}`}
            >
              {chain.charAt(0).toUpperCase() + chain.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4" data-testid="error-message">
          <div className="flex items-center gap-2 text-red-300">
            <AlertTriangle className="w-5 h-5" />
            <p>{error}</p>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
        </div>
      ) : (
        <>
          {/* Balance Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {balances.map((balance, index) => (
              <div
                key={index}
                className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-purple-500/20 p-6 card-hover"
                data-testid={`balance-card-${balance.chain}`}
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white capitalize">
                    {balance.chain}
                  </h3>
                  <Shield className="w-5 h-5 text-purple-400" />
                </div>

                {balance.error ? (
                  <div className="text-red-300 text-sm">
                    <p>{balance.error}</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div>
                      <p className="text-white/60 text-sm mb-1">Total Balance</p>
                      <p className="text-2xl font-bold text-white" data-testid={`balance-total-${balance.chain}`}>
                        {formatBalance(balance.total)} {getChainSymbol(balance.chain)}
                      </p>
                    </div>

                    <div className="grid grid-cols-2 gap-3 pt-3 border-t border-white/10">
                      <div>
                        <p className="text-white/60 text-xs mb-1">Free</p>
                        <p className="text-sm text-white font-mono">
                          {formatBalance(balance.free)}
                        </p>
                      </div>
                      <div>
                        <p className="text-white/60 text-xs mb-1">Reserved</p>
                        <p className="text-sm text-white font-mono">
                          {formatBalance(balance.reserved)}
                        </p>
                      </div>
                    </div>

                    <div className="pt-2">
                      <p className="text-white/60 text-xs mb-1">Transferable</p>
                      <p className="text-sm text-green-400 font-mono">
                        {formatBalance(balance.transferable)} {getChainSymbol(balance.chain)}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Summary Stats */}
          <div className="bg-gradient-to-r from-purple-600/20 to-pink-600/20 backdrop-blur-lg rounded-xl border border-purple-500/30 p-6">
            <div className="flex items-center gap-3 mb-4">
              <TrendingUp className="w-6 h-6 text-purple-400" />
              <h3 className="text-xl font-bold text-white">Portfolio Summary</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <p className="text-white/60 text-sm mb-1">Active Chains</p>
                <p className="text-3xl font-bold text-white" data-testid="active-chains-count">
                  {balances.filter(b => !b.error).length}
                </p>
              </div>
              <div>
                <p className="text-white/60 text-sm mb-1">Total Accounts</p>
                <p className="text-3xl font-bold text-white">1</p>
              </div>
              <div>
                <p className="text-white/60 text-sm mb-1">Security Status</p>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                  <p className="text-2xl font-bold text-green-400">Protected</p>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Dashboard;
