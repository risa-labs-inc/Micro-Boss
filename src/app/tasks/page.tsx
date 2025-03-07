"use client";

import { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import TaskList from '@/components/dashboard/TaskList';
import { Task } from '@/lib/types';
import { TaskApi } from '@/lib/services/api';
import { toast } from 'react-hot-toast';

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch tasks on component mount
  useEffect(() => {
    fetchTasks();
  }, []);

  // Function to fetch tasks
  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const fetchedTasks = await TaskApi.getTasks();
      setTasks(fetchedTasks);
    } catch (err) {
      console.error('Error fetching tasks:', err);
      setError('Failed to load tasks. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Handle starting a task
  const handleStartTask = async (taskId: string) => {
    try {
      await TaskApi.startTask(taskId);
      toast.success('Task started successfully');
      // Refresh task list
      fetchTasks();
    } catch (err) {
      console.error('Error starting task:', err);
      toast.error('Failed to start task. Please try again.');
    }
  };

  // Handle canceling a task (placeholder - API endpoint needs to be implemented)
  const handleCancelTask = async (taskId: string) => {
    try {
      // This would call an API endpoint to cancel the task
      // await TaskApi.cancelTask(taskId);
      toast.success('Task canceled successfully');
      // For now, just refresh the task list
      fetchTasks();
    } catch (err) {
      console.error('Error canceling task:', err);
      toast.error('Failed to cancel task. Please try again.');
    }
  };

  return (
    <MainLayout>
      <div className="container mx-auto">
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6" role="alert">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
              <div className="ml-auto pl-3">
                <button 
                  onClick={fetchTasks} 
                  className="text-sm text-red-700 hover:text-red-900 underline"
                >
                  Retry
                </button>
              </div>
            </div>
          </div>
        )}

        <TaskList 
          tasks={tasks} 
          isLoading={loading} 
          onStartTask={handleStartTask} 
          onCancelTask={handleCancelTask} 
        />
      </div>
    </MainLayout>
  );
} 