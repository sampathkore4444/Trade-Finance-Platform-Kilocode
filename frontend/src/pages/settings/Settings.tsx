import { useState } from 'react'
import { Save, Shield, Bell, Mail, Lock, Settings, Globe, DollarSign, FileText } from 'lucide-react'

const tabs = [
  { id: 'general', label: 'General', icon: Settings },
  { id: 'security', label: 'Security', icon: Shield },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'limits', label: 'Limits & Fees', icon: DollarSign },
  { id: 'integrations', label: 'Integrations', icon: Globe },
]

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('general')
  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Settings</h1>
          <p className="text-sm text-secondary-500 mt-1">Configure system settings and preferences</p>
        </div>
        <button onClick={handleSave} className="btn-primary">
          <Save className="w-4 h-4 mr-2" />
          {saved ? 'Saved!' : 'Save Changes'}
        </button>
      </div>

      <div className="flex space-x-6">
        {/* Sidebar */}
        <div className="w-56 flex-shrink-0">
          <nav className="space-y-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                  activeTab === tab.id
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-secondary-600 hover:bg-secondary-50'
                }`}
              >
                <tab.icon className="w-5 h-5 mr-3" />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1">
          {activeTab === 'general' && (
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-secondary-900">General Settings</h3>
              </div>
              <div className="card-body space-y-6">
                <div>
                  <label className="label">Organization Name</label>
                  <input type="text" className="input" defaultValue="Trade Finance Bank" />
                </div>
                <div>
                  <label className="label">Default Currency</label>
                  <select className="input">
                    <option value="USD">USD - US Dollar</option>
                    <option value="EUR">EUR - Euro</option>
                    <option value="GBP">GBP - British Pound</option>
                  </select>
                </div>
                <div>
                  <label className="label">Timezone</label>
                  <select className="input">
                    <option value="UTC">UTC</option>
                    <option value="America/New_York">Eastern Time</option>
                    <option value="Europe/London">London</option>
                    <option value="Asia/Singapore">Singapore</option>
                  </select>
                </div>
                <div>
                  <label className="label">Date Format</label>
                  <select className="input">
                    <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                    <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                    <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-secondary-900">Security Settings</h3>
              </div>
              <div className="card-body space-y-6">
                <div className="flex items-center justify-between p-4 bg-secondary-50 rounded-lg">
                  <div>
                    <p className="font-medium text-secondary-900">Two-Factor Authentication</p>
                    <p className="text-sm text-secondary-500">Require 2FA for all users</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" defaultChecked />
                    <div className="w-11 h-6 bg-secondary-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                  </label>
                </div>
                <div className="flex items-center justify-between p-4 bg-secondary-50 rounded-lg">
                  <div>
                    <p className="font-medium text-secondary-900">Session Timeout</p>
                    <p className="text-sm text-secondary-500">Auto logout after inactivity</p>
                  </div>
                  <select className="input w-auto">
                    <option value="15">15 minutes</option>
                    <option value="30">30 minutes</option>
                    <option value="60">1 hour</option>
                  </select>
                </div>
                <div>
                  <label className="label">Password Policy</label>
                  <div className="space-y-2">
                    <label className="flex items-center">
                      <input type="checkbox" defaultChecked className="mr-2" />
                      Minimum 8 characters
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" defaultChecked className="mr-2" />
                      Require uppercase letters
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" defaultChecked className="mr-2" />
                      Require numbers
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-2" />
                      Require special characters
                    </label>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-secondary-900">Notification Preferences</h3>
              </div>
              <div className="card-body space-y-4">
                {[
                  { label: 'LC Status Changes', desc: 'Get notified when LC status changes' },
                  { label: 'Approval Required', desc: 'Alert when approval is needed' },
                  { label: 'Document Expiry', desc: 'Warning before documents expire' },
                  { label: 'Payment Received', desc: 'Confirmation when payment is processed' },
                  { label: 'Risk Alerts', desc: 'Critical risk notifications' },
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between p-4 bg-secondary-50 rounded-lg">
                    <div>
                      <p className="font-medium text-secondary-900">{item.label}</p>
                      <p className="text-sm text-secondary-500">{item.desc}</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" defaultChecked className="sr-only peer" />
                      <div className="w-11 h-6 bg-secondary-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                    </label>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'limits' && (
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-secondary-900">Transaction Limits & Fees</h3>
              </div>
              <div className="card-body space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="label">Minimum LC Amount</label>
                    <input type="number" className="input" defaultValue="10000" />
                  </div>
                  <div>
                    <label className="label">Maximum LC Amount</label>
                    <input type="number" className="input" defaultValue="10000000" />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="label">Default LC Fee (%)</label>
                    <input type="number" step="0.01" className="input" defaultValue="0.5" />
                  </div>
                  <div>
                    <label className="label">Amendment Fee</label>
                    <input type="number" className="input" defaultValue="150" />
                  </div>
                </div>
                <div>
                  <label className="label">Approval Thresholds</label>
                  <table className="table mt-2">
                    <thead>
                      <tr>
                        <th>Role</th>
                        <th>Max Approval Amount</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>Credit Officer</td>
                        <td><input type="number" className="input" defaultValue="100000" /></td>
                      </tr>
                      <tr>
                        <td>Senior Manager</td>
                        <td><input type="number" className="input" defaultValue="500000" /></td>
                      </tr>
                      <tr>
                        <td>Administrator</td>
                        <td><input type="number" className="input" defaultValue="10000000" /></td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'integrations' && (
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold text-secondary-900">External Integrations</h3>
              </div>
              <div className="card-body space-y-4">
                {[
                  { name: 'SWIFT Network', desc: 'International payment messaging', connected: true },
                  { name: 'Trade Registry', desc: 'Government trade documentation', connected: false },
                  { name: 'Credit Bureau', desc: 'Credit reporting agency', connected: true },
                  { name: 'ERP System', desc: 'Enterprise resource planning', connected: false },
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between p-4 bg-secondary-50 rounded-lg">
                    <div className="flex items-center">
                      <Globe className="w-8 h-8 text-secondary-400 mr-4" />
                      <div>
                        <p className="font-medium text-secondary-900">{item.name}</p>
                        <p className="text-sm text-secondary-500">{item.desc}</p>
                      </div>
                    </div>
                    <span className={`badge ${item.connected ? 'badge-success' : 'badge-secondary'}`}>
                      {item.connected ? 'Connected' : 'Not Connected'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
