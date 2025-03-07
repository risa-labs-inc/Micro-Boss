"use client";

import { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import Link from 'next/link';
import { Task, TaskStatus } from '@/lib/types';
import { TaskApi } from '@/lib/services/api';
import TaskCard from '@/components/dashboard/TaskCard';

// Dashboard Stat Card component
const StatCard = ({ 
  title, 
  value, 
  icon, 
  bgColor, 
  textColor,
  change
}: { 
  title: string, 
  value: number | string, 
  icon: React.ReactNode, 
  bgColor: string, 
  textColor: string,
  change?: { value: number, label: string }
}) => (
  <div className={`${bgColor} rounded-lg shadow-sm p-4`}>
    <div className="flex justify-between items-start">
      <div>
        <p className="text-sm font-medium mb-1 text-gray-700">{title}</p>
        <h3 className={`text-2xl font-bold ${textColor}`}>{value}</h3>
        {change && (
          <p className={`text-xs mt-1 ${change.value >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {change.value > 0 ? '↑' : '↓'} {Math.abs(change.value)}% {change.label}
          </p>
        )}
      </div>
      <div className={`rounded-full p-2 ${textColor} bg-white bg-opacity-30`}>
        {icon}
      </div>
    </div>
  </div>
);

// Dashboard component
export default function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState({
    total: 0,
    completed: 0,
    running: 0,
    pending: 0,
    failed: 0
  });

  // Fetch tasks and calculate stats
  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setLoading(true);
        const response = await TaskApi.getTasks();
        setTasks(response);
        
        // Calculate statistics
        const newStats = {
          total: response.length,
          completed: response.filter(task => task.status === 'completed').length,
          running: response.filter(task => task.status === 'running').length,
          pending: response.filter(task => task.status === 'pending').length,
          failed: response.filter(task => task.status === 'failed').length
        };
        setStats(newStats);
        
      } catch (err) {
        console.error('Error fetching tasks:', err);
        setError('Failed to load dashboard data.');
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, []);

  // Get recent tasks (last 4)
  const recentTasks = tasks
    .sort((a, b) => new Date(b.updated_at || b.created_at).getTime() - new Date(a.updated_at || a.created_at).getTime())
    .slice(0, 4);

  // Calculate success rate
  const successRate = stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0;
  
  // Get task by status
  const getTasksByStatus = (status: TaskStatus) => {
    return tasks.filter(task => task.status === status);
  };

  return (
    <MainLayout>
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">Dashboard</h1>
        <p className="text-gray-600">
          Welcome to the Microboss dashboard. Here's an overview of your tasks and system status.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard 
          title="Total Tasks" 
          value={stats.total}
          icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>}
          bgColor="bg-blue-50"
          textColor="text-blue-600"
          change={{ value: 12, label: 'from last month' }}
        />
        <StatCard 
          title="Running Tasks" 
          value={stats.running}
          icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
          bgColor="bg-yellow-50"
          textColor="text-yellow-600"
        />
        <StatCard 
          title="Completed Tasks" 
          value={stats.completed}
          icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
          bgColor="bg-green-50"
          textColor="text-green-600"
          change={{ value: 8, label: 'from last month' }}
        />
        <StatCard 
          title="Success Rate" 
          value={`${successRate}%`}
          icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>}
          bgColor="bg-purple-50"
          textColor="text-purple-600"
        />
      </div>

      {/* Recent Tasks and Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-medium">Recent Tasks</h2>
              <Link href="/tasks" className="text-blue-600 hover:underline text-sm">
                View All <span aria-hidden="true">→</span>
              </Link>
            </div>
            
            {loading ? (
              <div className="animate-pulse space-y-4">
                {[1, 2, 3].map(i => (
                  <div key={i} className="h-20 bg-gray-200 rounded"></div>
                ))}
              </div>
            ) : error ? (
              <div className="text-center py-4 text-red-500">{error}</div>
            ) : recentTasks.length === 0 ? (
              <div className="text-center py-10 text-gray-500 border border-dashed border-gray-300 rounded-md">
                <p>No tasks available yet.</p>
                <Link href="/tasks/new" className="mt-2 inline-block text-blue-600 hover:underline">
                  Create your first task
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {recentTasks.map(task => (
                  <div key={task.task_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition">
                    <div className="flex justify-between">
                      <Link href={`/tasks/${task.task_id}`} className="font-medium text-blue-600 hover:underline">
                        {task.description}
                      </Link>
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        task.status === 'completed' ? 'bg-green-100 text-green-800' :
                        task.status === 'running' ? 'bg-blue-100 text-blue-800' :
                        task.status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {task.status}
                      </span>
                    </div>
                    <div className="mt-2 text-sm text-gray-500">
                      Created: {new Date(task.created_at).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
        
        {/* Quick Actions & Stats */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium mb-4">Quick Actions</h2>
            <div className="space-y-2">
              <Link href="/tasks/new" className="block w-full text-center bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded">
                Create New Task
              </Link>
              <Link href="/tasks" className="block w-full text-center bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 font-medium py-2 px-4 rounded">
                View All Tasks
              </Link>
              <Link href="/settings" className="block w-full text-center bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 font-medium py-2 px-4 rounded">
                Settings
              </Link>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium mb-4">Tasks by Status</h2>
            {loading ? (
              <div className="animate-pulse space-y-2">
                <div className="h-4 bg-gray-200 rounded"></div>
                <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                <div className="h-4 bg-gray-200 rounded w-4/6"></div>
              </div>
            ) : (
              <div className="space-y-3">
                {/* Pending Tasks */}
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium">Pending</span>
                    <span>{stats.pending}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-gray-500 h-2 rounded-full" style={{ width: `${(stats.pending / stats.total) * 100}%` }}></div>
                  </div>
                </div>
                
                {/* Running Tasks */}
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium">Running</span>
                    <span>{stats.running}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${(stats.running / stats.total) * 100}%` }}></div>
                  </div>
                </div>
                
                {/* Completed Tasks */}
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium">Completed</span>
                    <span>{stats.completed}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{ width: `${(stats.completed / stats.total) * 100}%` }}></div>
                  </div>
                </div>
                
                {/* Failed Tasks */}
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium">Failed</span>
                    <span>{stats.failed}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-red-500 h-2 rounded-full" style={{ width: `${(stats.failed / stats.total) * 100}%` }}></div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* System Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-medium mb-4">System Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="flex items-center">
              <div className="rounded-full h-3 w-3 bg-green-500 mr-2"></div>
              <h3 className="text-sm font-medium">API Services</h3>
            </div>
            <p className="mt-2 text-sm text-gray-600">All systems operational</p>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="flex items-center">
              <div className="rounded-full h-3 w-3 bg-green-500 mr-2"></div>
              <h3 className="text-sm font-medium">Task Processing</h3>
            </div>
            <p className="mt-2 text-sm text-gray-600">All systems operational</p>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="flex items-center">
              <div className="rounded-full h-3 w-3 bg-green-500 mr-2"></div>
              <h3 className="text-sm font-medium">Database</h3>
            </div>
            <p className="mt-2 text-sm text-gray-600">All systems operational</p>
          </div>
        </div>
      </div>
    </MainLayout>
  );
} 