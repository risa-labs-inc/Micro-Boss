"use client";

import { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { useForm } from 'react-hook-form';
import { toast } from 'react-hot-toast';

interface SettingsFormData {
  apiKey: string;
  baseUrl: string;
  timeout: number;
  logLevel: 'debug' | 'info' | 'warning' | 'error';
  enableNotifications: boolean;
  theme: 'light' | 'dark' | 'system';
}

export default function SettingsPage() {
  const [showApiKey, setShowApiKey] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  
  // Initialize form with react-hook-form
  const { register, handleSubmit, formState: { errors, isDirty }, reset } = useForm<SettingsFormData>({
    defaultValues: {
      apiKey: '',
      baseUrl: '',
      timeout: 30,
      logLevel: 'info',
      enableNotifications: true,
      theme: 'light'
    }
  });
  
  // Load saved settings from localStorage on component mount
  useEffect(() => {
    try {
      const savedSettings = localStorage.getItem('microboss_settings');
      if (savedSettings) {
        const settings = JSON.parse(savedSettings);
        reset(settings);
      }
    } catch (err) {
      console.error('Error loading settings:', err);
    }
  }, [reset]);
  
  // Toggle API key visibility
  const toggleApiKeyVisibility = () => {
    setShowApiKey(!showApiKey);
  };
  
  // Handle form submission
  const onSubmit = async (data: SettingsFormData) => {
    try {
      setIsSaving(true);
      
      // Save settings to localStorage
      localStorage.setItem('microboss_settings', JSON.stringify(data));
      
      // In a real app, you might also want to save to a backend API
      // await api.saveSettings(data);
      
      // Show success message
      toast.success('Settings saved successfully');
    } catch (err) {
      console.error('Error saving settings:', err);
      toast.error('Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };
  
  // Reset form to default values
  const handleReset = () => {
    const defaultValues = {
      apiKey: '',
      baseUrl: 'http://localhost:5000',
      timeout: 30,
      logLevel: 'info' as const,
      enableNotifications: true,
      theme: 'light' as const
    };
    
    reset(defaultValues);
    localStorage.setItem('microboss_settings', JSON.stringify(defaultValues));
    toast.success('Settings reset to defaults');
  };

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
            <p className="text-gray-600 mt-1">Manage your application settings and preferences</p>
          </div>
          
          <form onSubmit={handleSubmit(onSubmit)}>
            {/* API Settings Section */}
            <div className="mb-8">
              <h2 className="text-lg font-semibold mb-4 pb-2 border-b">API Configuration</h2>
              
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="apiKey">
                  API Key
                </label>
                <div className="flex">
                  <input
                    className="shadow appearance-none border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline flex-1"
                    id="apiKey"
                    type={showApiKey ? "text" : "password"}
                    placeholder="Enter your API key"
                    {...register('apiKey')}
                  />
                  <button
                    type="button"
                    onClick={toggleApiKeyVisibility}
                    className="ml-2 bg-gray-200 hover:bg-gray-300 text-gray-800 py-2 px-4 rounded"
                  >
                    {showApiKey ? "Hide" : "Show"}
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Your API key for third-party services. Keep this private.
                </p>
              </div>
              
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="baseUrl">
                  API Base URL
                </label>
                <input
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  id="baseUrl"
                  type="text"
                  placeholder="http://localhost:5000"
                  {...register('baseUrl')}
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="timeout">
                  Request Timeout (seconds)
                </label>
                <input
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  id="timeout"
                  type="number"
                  min="5"
                  max="120"
                  {...register('timeout', { valueAsNumber: true })}
                />
              </div>
            </div>
            
            {/* Application Settings Section */}
            <div className="mb-8">
              <h2 className="text-lg font-semibold mb-4 pb-2 border-b">Application Settings</h2>
              
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="logLevel">
                  Log Level
                </label>
                <select
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  id="logLevel"
                  {...register('logLevel')}
                >
                  <option value="debug">Debug</option>
                  <option value="info">Info</option>
                  <option value="warning">Warning</option>
                  <option value="error">Error</option>
                </select>
              </div>
              
              <div className="mb-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="mr-2"
                    {...register('enableNotifications')}
                  />
                  <span className="text-gray-700 text-sm font-bold">Enable Notifications</span>
                </label>
              </div>
              
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="theme">
                  Theme
                </label>
                <select
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  id="theme"
                  {...register('theme')}
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="system">System</option>
                </select>
              </div>
            </div>
            
            {/* Action Buttons */}
            <div className="flex items-center justify-end">
              <button
                type="button"
                onClick={handleReset}
                className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded mr-2"
              >
                Reset to Defaults
              </button>
              <button
                type="submit"
                disabled={isSaving || !isDirty}
                className={`bg-blue-600 ${isSaving || !isDirty ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-700'} text-white font-bold py-2 px-4 rounded`}
              >
                {isSaving ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Saving...
                  </>
                ) : (
                  'Save Settings'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </MainLayout>
  );
} 