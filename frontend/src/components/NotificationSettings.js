// © 2025 Deepak Raghunath Raut — All rights reserved. MIT Licensed.
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bell, Save, Loader2, CheckCircle, Mail, MessageSquare, Smartphone, Webhook } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const NotificationSettings = ({ account }) => {
  const [preferences, setPreferences] = useState({
    transfer: { channels: [], enabled: true },
    staking: { channels: [], enabled: true },
    governance: { channels: [], enabled: true },
    security_alert: { channels: ['discord', 'email'], enabled: true }
  });
  
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [testResult, setTestResult] = useState(null);

  const eventTypes = [
    { id: 'transfer', name: 'Transfers', description: 'Token transfers and balance changes' },
    { id: 'staking', name: 'Staking', description: 'Staking rewards and nominations' },
    { id: 'governance', name: 'Governance', description: 'Voting and proposals' },
    { id: 'security_alert', name: 'Security Alerts', description: 'High-risk transactions and warnings' }
  ];

  const channels = [
    { id: 'email', name: 'Email', icon: Mail },
    { id: 'discord', name: 'Discord', icon: MessageSquare },
    { id: 'mobile', name: 'Mobile Push', icon: Smartphone },
    { id: 'webhook', name: 'Webhook', icon: Webhook }
  ];

  useEffect(() => {
    if (account) {
      loadPreferences();
    }
  }, [account]);

  const loadPreferences = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/notifications/preferences/${account.address}`);
      
      if (response.data.preferences && response.data.preferences.length > 0) {
        const prefs = {};
        response.data.preferences.forEach(pref => {
          prefs[pref.event_type] = {
            channels: pref.channels,
            enabled: pref.enabled
          };
        });
        setPreferences(prev => ({ ...prev, ...prefs }));
      }
    } catch (err) {
      console.error('Failed to load preferences:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleChannel = (eventType, channel) => {
    setPreferences(prev => {
      const currentChannels = prev[eventType].channels;
      const newChannels = currentChannels.includes(channel)
        ? currentChannels.filter(c => c !== channel)
        : [...currentChannels, channel];
      
      return {
        ...prev,
        [eventType]: {
          ...prev[eventType],
          channels: newChannels
        }
      };
    });
    setSaved(false);
  };

  const toggleEventEnabled = (eventType) => {
    setPreferences(prev => ({
      ...prev,
      [eventType]: {
        ...prev[eventType],
        enabled: !prev[eventType].enabled
      }
    }));
    setSaved(false);
  };

  const savePreferences = async () => {
    setSaving(true);
    
    try {
      // Save each preference
      const savePromises = Object.entries(preferences).map(([eventType, pref]) =>
        axios.post(`${API}/notifications/preferences`, {
          user_id: account.address,
          event_type: eventType,
          channels: pref.channels,
          enabled: pref.enabled
        })
      );
      
      await Promise.all(savePromises);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error('Failed to save preferences:', err);
    } finally {
      setSaving(false);
    }
  };

  const testNotification = async () => {
    setTestResult(null);
    
    try {
      const response = await axios.post(`${API}/notify`, {
        event_type: 'security_alert',
        channels: preferences.security_alert.channels,
        payload: {
          message: 'Test notification from SAFDO',
          timestamp: new Date().toISOString()
        },
        user_id: account.address
      });
      
      setTestResult(response.data);
    } catch (err) {
      console.error('Test notification failed:', err);
      setTestResult({ status: 'error', error: err.message });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2" data-testid="notifications-title">Notification Preferences</h2>
          <p className="text-white/60">Configure how you want to receive alerts</p>
        </div>
        <button
          onClick={savePreferences}
          disabled={saving || saved}
          className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:from-gray-600 disabled:to-gray-600 text-white font-semibold rounded-lg transition-all flex items-center gap-2"
          data-testid="save-preferences-btn"
        >
          {saving ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : saved ? (
            <CheckCircle className="w-5 h-5" />
          ) : (
            <Save className="w-5 h-5" />
          )}
          {saving ? 'Saving...' : saved ? 'Saved!' : 'Save Preferences'}
        </button>
      </div>

      {/* DRY RUN Notice */}
      <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Bell className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-yellow-300 font-semibold mb-1">DRY-RUN Mode Active</p>
            <p className="text-yellow-200/80 text-sm">
              Notifications are currently in testing mode. They will be logged but not sent. See backend logs for dispatch targets.
            </p>
          </div>
        </div>
      </div>

      {/* Event Type Settings */}
      <div className="space-y-4">
        {eventTypes.map(event => (
          <div
            key={event.id}
            className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-purple-500/20 p-6"
            data-testid={`event-settings-${event.id}`}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-xl font-bold text-white">{event.name}</h3>
                  <button
                    onClick={() => toggleEventEnabled(event.id)}
                    className={`px-3 py-1 rounded-full text-xs font-semibold transition ${
                      preferences[event.id].enabled
                        ? 'bg-green-500/20 text-green-300 border border-green-500/30'
                        : 'bg-gray-500/20 text-gray-400 border border-gray-500/30'
                    }`}
                    data-testid={`toggle-event-${event.id}`}
                  >
                    {preferences[event.id].enabled ? 'Enabled' : 'Disabled'}
                  </button>
                </div>
                <p className="text-white/60 text-sm">{event.description}</p>
              </div>
            </div>

            {preferences[event.id].enabled && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {channels.map(channel => {
                  const Icon = channel.icon;
                  const isSelected = preferences[event.id].channels.includes(channel.id);
                  
                  return (
                    <button
                      key={channel.id}
                      onClick={() => toggleChannel(event.id, channel.id)}
                      className={`p-4 rounded-lg border-2 transition ${
                        isSelected
                          ? 'bg-purple-600/30 border-purple-500 text-white'
                          : 'bg-slate-700/30 border-slate-600 text-white/60 hover:border-slate-500'
                      }`}
                      data-testid={`channel-${event.id}-${channel.id}`}
                    >
                      <Icon className="w-6 h-6 mx-auto mb-2" />
                      <p className="text-sm font-semibold">{channel.name}</p>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Test Notification */}
      <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-purple-500/20 p-6">
        <h3 className="text-xl font-bold text-white mb-4">Test Notification</h3>
        <p className="text-white/60 mb-4">
          Send a test security alert to verify your notification channels are configured correctly.
        </p>
        <button
          onClick={testNotification}
          className="px-6 py-3 bg-purple-600 hover:bg-purple-500 text-white font-semibold rounded-lg transition flex items-center gap-2"
          data-testid="test-notification-btn"
        >
          <Bell className="w-5 h-5" />
          Send Test Alert
        </button>

        {testResult && (
          <div className="mt-4 p-4 bg-slate-900/50 rounded-lg" data-testid="test-result">
            <p className="text-white font-semibold mb-2">Test Result:</p>
            <pre className="text-white/80 text-sm overflow-auto">
              {JSON.stringify(testResult, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default NotificationSettings;
