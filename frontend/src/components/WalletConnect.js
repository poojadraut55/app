// © 2025 Deepak Raghunath Raut — All rights reserved. MIT Licensed.
import React, { useState, useEffect } from 'react';
import { web3Accounts, web3Enable, web3FromAddress } from '@polkadot/extension-dapp';
import { Shield, Wallet, AlertCircle } from 'lucide-react';

const WalletConnect = ({ onConnect }) => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [extensionInstalled, setExtensionInstalled] = useState(true);

  useEffect(() => {
    checkExtension();
  }, []);

  const checkExtension = async () => {
    try {
      const extensions = await web3Enable('SAFDO Crypto Shield');
      if (extensions.length === 0) {
        setExtensionInstalled(false);
        setError('No Polkadot.js extension detected');
      }
    } catch (err) {
      console.error('Extension check error:', err);
      setExtensionInstalled(false);
      setError('Failed to detect wallet extension');
    }
  };

  const connectWallet = async () => {
    setLoading(true);
    setError('');

    try {
      // Enable extension
      const extensions = await web3Enable('SAFDO Crypto Shield');
      
      if (extensions.length === 0) {
        throw new Error('No extension installed');
      }

      // Get accounts
      const allAccounts = await web3Accounts();
      
      if (allAccounts.length === 0) {
        throw new Error('No accounts found in wallet');
      }

      setAccounts(allAccounts);
    } catch (err) {
      console.error('Wallet connection error:', err);
      setError(err.message || 'Failed to connect wallet');
    } finally {
      setLoading(false);
    }
  };

  const selectAccount = async (account) => {
    try {
      // Get injector for signing
      const injector = await web3FromAddress(account.address);
      
      // Pass account and injector to parent
      onConnect({
        ...account,
        injector
      });
    } catch (err) {
      console.error('Account selection error:', err);
      setError('Failed to select account');
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl border border-purple-500/20 p-8 card-hover">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-purple-500/20 rounded-full mb-4 pulse-glow">
            <Shield className="w-10 h-10 text-purple-400" />
          </div>
          <h2 className="text-3xl font-bold text-white mb-2" data-testid="wallet-connect-title">
            Connect Your Wallet
          </h2>
          <p className="text-white/60">
            Connect your Polkadot wallet to access SAFDO security features
          </p>
        </div>

        {!extensionInstalled && (
          <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4 mb-6">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-yellow-300 font-semibold mb-1">Polkadot.js Extension Required</p>
                <p className="text-yellow-200/80 text-sm mb-3">
                  Please install the Polkadot.js browser extension to continue.
                </p>
                <a
                  href="https://polkadot.js.org/extension/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block px-4 py-2 bg-yellow-500/20 hover:bg-yellow-500/30 text-yellow-300 rounded-lg text-sm transition"
                >
                  Install Extension
                </a>
              </div>
            </div>
          </div>
        )}

        {error && accounts.length === 0 && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-6" data-testid="error-message">
            <div className="flex items-center gap-2 text-red-300">
              <AlertCircle className="w-5 h-5" />
              <p>{error}</p>
            </div>
          </div>
        )}

        {accounts.length === 0 ? (
          <button
            onClick={connectWallet}
            disabled={loading || !extensionInstalled}
            className="w-full flex items-center justify-center gap-3 px-6 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:from-gray-600 disabled:to-gray-600 text-white font-semibold rounded-lg transition-all transform hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed"
            data-testid="connect-wallet-btn"
          >
            <Wallet className="w-5 h-5" />
            {loading ? 'Connecting...' : 'Connect Wallet'}
          </button>
        ) : (
          <div className="space-y-3">
            <p className="text-white/80 font-semibold mb-3">Select an account:</p>
            {accounts.map((account, index) => (
              <button
                key={account.address}
                onClick={() => selectAccount(account)}
                className="w-full p-4 bg-slate-700/50 hover:bg-slate-700 border border-purple-500/20 hover:border-purple-500/40 rounded-lg transition text-left"
                data-testid={`account-option-${index}`}
              >
                <p className="text-white font-semibold mb-1">{account.meta.name}</p>
                <p className="text-white/60 text-sm font-mono">{account.address}</p>
              </button>
            ))}
          </div>
        )}

        <div className="mt-8 pt-6 border-t border-white/10">
          <h3 className="text-white font-semibold mb-3">Supported Networks</h3>
          <div className="flex gap-3">
            <div className="flex-1 px-4 py-2 bg-purple-500/10 border border-purple-500/30 rounded-lg text-center">
              <p className="text-purple-300 text-sm font-semibold">Polkadot</p>
            </div>
            <div className="flex-1 px-4 py-2 bg-purple-500/10 border border-purple-500/30 rounded-lg text-center">
              <p className="text-purple-300 text-sm font-semibold">Kusama</p>
            </div>
            <div className="flex-1 px-4 py-2 bg-purple-500/10 border border-purple-500/30 rounded-lg text-center">
              <p className="text-purple-300 text-sm font-semibold">Westend</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WalletConnect;
