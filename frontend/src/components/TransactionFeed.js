// © 2025 Deepak Raghunath Raut — All rights reserved. MIT Licensed.
import React, { useState } from 'react';
import axios from 'axios';
import { Activity, AlertTriangle, CheckCircle, XCircle, Loader2 } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TransactionFeed = ({ account }) => {
  const [testTransaction, setTestTransaction] = useState({
    from_address: account?.address || '',
    to_address: '',
    amount: '',
    chain: 'polkadot',
    method: ''
  });
  
  const [riskResult, setRiskResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (field, value) => {
    setTestTransaction(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const analyzeTransaction = async () => {
    setLoading(true);
    setError('');
    setRiskResult(null);

    try {
      const response = await axios.post(`${API}/risk-score`, testTransaction);
      setRiskResult(response.data);
    } catch (err) {
      console.error('Risk analysis error:', err);
      setError(err.response?.data?.detail || 'Failed to analyze transaction');
    } finally {
      setLoading(false);
    }
  };

  const getRiskIcon = (level) => {
    switch (level) {
      case 'LOW':
        return <CheckCircle className="w-6 h-6 text-green-400" />;
      case 'MEDIUM':
        return <AlertTriangle className="w-6 h-6 text-yellow-400" />;
      case 'HIGH':
        return <XCircle className="w-6 h-6 text-red-400" />;
      default:
        return <Activity className="w-6 h-6 text-purple-400" />;
    }
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'LOW':
        return 'risk-low';
      case 'MEDIUM':
        return 'risk-medium';
      case 'HIGH':
        return 'risk-high';
      default:
        return 'bg-slate-700';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white mb-2" data-testid="transactions-title">Transaction Risk Analyzer</h2>
        <p className="text-white/60">Test transaction risk scoring before sending</p>
      </div>

      {/* Transaction Input Form */}
      <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-purple-500/20 p-6">
        <h3 className="text-xl font-bold text-white mb-4">Transaction Details</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-white/80 text-sm font-semibold mb-2">
              From Address
            </label>
            <input
              type="text"
              value={testTransaction.from_address}
              onChange={(e) => handleInputChange('from_address', e.target.value)}
              className="w-full px-4 py-3 bg-slate-900/50 border border-purple-500/30 rounded-lg text-white font-mono text-sm focus:outline-none focus:border-purple-500"
              placeholder="5GrwvaEF5zXb26Fz..."
              data-testid="input-from-address"
            />
          </div>

          <div>
            <label className="block text-white/80 text-sm font-semibold mb-2">
              To Address
            </label>
            <input
              type="text"
              value={testTransaction.to_address}
              onChange={(e) => handleInputChange('to_address', e.target.value)}
              className="w-full px-4 py-3 bg-slate-900/50 border border-purple-500/30 rounded-lg text-white font-mono text-sm focus:outline-none focus:border-purple-500"
              placeholder="5FHneW46xGXgs5mUi..."
              data-testid="input-to-address"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-white/80 text-sm font-semibold mb-2">
                Amount (Planck)
              </label>
              <input
                type="text"
                value={testTransaction.amount}
                onChange={(e) => handleInputChange('amount', e.target.value)}
                className="w-full px-4 py-3 bg-slate-900/50 border border-purple-500/30 rounded-lg text-white font-mono text-sm focus:outline-none focus:border-purple-500"
                placeholder="1000000000000"
                data-testid="input-amount"
              />
              <p className="text-white/40 text-xs mt-1">1 DOT = 10^10 Planck</p>
            </div>

            <div>
              <label className="block text-white/80 text-sm font-semibold mb-2">
                Chain
              </label>
              <select
                value={testTransaction.chain}
                onChange={(e) => handleInputChange('chain', e.target.value)}
                className="w-full px-4 py-3 bg-slate-900/50 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:border-purple-500"
                data-testid="select-chain"
              >
                <option value="polkadot">Polkadot</option>
                <option value="kusama">Kusama</option>
                <option value="westend">Westend</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-white/80 text-sm font-semibold mb-2">
              Method (Optional)
            </label>
            <input
              type="text"
              value={testTransaction.method}
              onChange={(e) => handleInputChange('method', e.target.value)}
              className="w-full px-4 py-3 bg-slate-900/50 border border-purple-500/30 rounded-lg text-white font-mono text-sm focus:outline-none focus:border-purple-500"
              placeholder="transfer, proxy, staking.bond"
              data-testid="input-method"
            />
          </div>

          <button
            onClick={analyzeTransaction}
            disabled={loading || !testTransaction.from_address || !testTransaction.to_address || !testTransaction.amount}
            className="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:from-gray-600 disabled:to-gray-600 text-white font-bold rounded-lg transition-all transform hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            data-testid="analyze-transaction-btn"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Activity className="w-5 h-5" />
                Analyze Risk
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4" data-testid="error-message">
          <div className="flex items-center gap-2 text-red-300">
            <AlertTriangle className="w-5 h-5" />
            <p>{error}</p>
          </div>
        </div>
      )}

      {/* Risk Result Display */}
      {riskResult && (
        <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-purple-500/20 p-6" data-testid="risk-result">
          <h3 className="text-xl font-bold text-white mb-4">Risk Assessment</h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg">
              <div className="flex items-center gap-3">
                {getRiskIcon(riskResult.level)}
                <div>
                  <p className="text-white/60 text-sm">Risk Level</p>
                  <p className={`text-2xl font-bold px-4 py-1 rounded-lg inline-block ${getRiskColor(riskResult.level)}`} data-testid="risk-level">
                    {riskResult.level}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-white/60 text-sm">Risk Score</p>
                <p className="text-4xl font-bold text-white" data-testid="risk-score">{riskResult.score}/100</p>
              </div>
            </div>

            <div className="p-4 bg-slate-900/50 rounded-lg">
              <p className="text-white/80 font-semibold mb-3">Risk Factors:</p>
              <ul className="space-y-2">
                {riskResult.reasons.map((reason, index) => (
                  <li key={index} className="flex items-start gap-2 text-white/70" data-testid={`risk-reason-${index}`}>
                    <span className="text-purple-400 mt-1">•</span>
                    <span>{reason}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
              <p className="text-purple-300 text-sm">
                <strong>Note:</strong> This is a heuristic-based risk assessment. Always verify transaction details before signing.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TransactionFeed;
