"use client";

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useRouter } from 'next/navigation';
import MainLayout from '@/components/layout/MainLayout';
import { useAuth } from '@/lib/contexts/AuthContext';
import { User } from '@/lib/services/auth';

export default function ProfilePage() {
  const { user, updateProfile, logout, loading } = useAuth();
  const router = useRouter();
  const [isEditing, setIsEditing] = useState(false);
  
  // Initialize form with user data
  const { register, handleSubmit, formState: { errors, isDirty } } = useForm<Partial<User>>({
    defaultValues: {
      username: user?.username || '',
      email: user?.email || '',
    }
  });
  
  // Handle form submission
  const onSubmit = async (data: Partial<User>) => {
    try {
      await updateProfile(data);
      setIsEditing(false);
    } catch (err) {
      console.error('Profile update error:', err);
    }
  };
  
  // Handle logout
  const handleLogout = () => {
    logout();
    // Router redirect is handled in the auth context
  };
  
  // If not authenticated, redirect to login
  if (!user) {
    router.replace('/login');
    return <div className="flex justify-center items-center h-screen">Redirecting to login...</div>;
  }
  
  return (
    <MainLayout>
      <div className="bg-white shadow rounded-lg p-6 max-w-2xl mx-auto">
        <div className="mb-6 border-b pb-4">
          <h1 className="text-2xl font-bold text-gray-900">Your Profile</h1>
          <p className="text-gray-600 mt-1">Manage your account information</p>
        </div>
        
        <div className="flex flex-col md:flex-row items-start gap-8">
          {/* Profile Avatar */}
          <div className="flex flex-col items-center space-y-2 mb-4 md:mb-0">
            <div className="relative">
              <div className="h-32 w-32 bg-gray-200 rounded-full overflow-hidden">
                {user.avatar ? (
                  <img 
                    src={user.avatar} 
                    alt={`${user.username}'s avatar`} 
                    className="h-full w-full object-cover"
                  />
                ) : (
                  <div className="flex items-center justify-center h-full w-full bg-blue-500 text-white text-4xl font-bold">
                    {user.username?.charAt(0).toUpperCase() || 'U'}
                  </div>
                )}
              </div>
              <button 
                className="absolute bottom-0 right-0 bg-gray-800 text-white p-1 rounded-full"
                title="Change avatar"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>
            </div>
            <div className="text-center">
              <p className="font-medium text-lg text-gray-900">{user.username}</p>
              <p className="text-sm text-gray-500">{user.role}</p>
            </div>
          </div>
          
          {/* Profile Info */}
          <div className="flex-1">
            {isEditing ? (
              <form onSubmit={handleSubmit(onSubmit)}>
                <div className="space-y-4">
                  <div>
                    <label htmlFor="username" className="block text-sm font-medium text-gray-700">Username</label>
                    <input
                      id="username"
                      type="text"
                      className={`mt-1 block w-full px-3 py-2 border ${
                        errors.username ? 'border-red-300' : 'border-gray-300'
                      } rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500`}
                      {...register('username', { 
                        required: 'Username is required',
                        minLength: { value: 3, message: 'Username must be at least 3 characters' }
                      })}
                    />
                    {errors.username && (
                      <p className="mt-1 text-xs text-red-600">{errors.username.message}</p>
                    )}
                  </div>
                  
                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email</label>
                    <input
                      id="email"
                      type="email"
                      className={`mt-1 block w-full px-3 py-2 border ${
                        errors.email ? 'border-red-300' : 'border-gray-300'
                      } rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500`}
                      {...register('email', { 
                        required: 'Email is required',
                        pattern: { 
                          value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                          message: 'Invalid email address' 
                        }
                      })}
                    />
                    {errors.email && (
                      <p className="mt-1 text-xs text-red-600">{errors.email.message}</p>
                    )}
                  </div>
                  
                  <div className="flex space-x-3 justify-end pt-4">
                    <button
                      type="button"
                      onClick={() => setIsEditing(false)}
                      className="px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={loading || !isDirty}
                      className={`px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white ${
                        loading || !isDirty ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
                      }`}
                    >
                      {loading ? 'Saving...' : 'Save Changes'}
                    </button>
                  </div>
                </div>
              </form>
            ) : (
              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Username</h3>
                  <p className="mt-1 text-sm text-gray-900">{user.username}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Email</h3>
                  <p className="mt-1 text-sm text-gray-900">{user.email}</p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Role</h3>
                  <p className="mt-1 text-sm text-gray-900 capitalize">{user.role}</p>
                </div>
                
                <div className="pt-4 flex space-x-3">
                  <button
                    onClick={() => setIsEditing(true)}
                    className="px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                  >
                    Edit Profile
                  </button>
                  <button
                    onClick={handleLogout}
                    className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700"
                  >
                    Sign Out
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  );
} 