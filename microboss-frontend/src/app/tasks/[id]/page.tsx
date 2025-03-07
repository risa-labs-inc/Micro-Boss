'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import taskService from '@/services/TaskService';
import { Task } from '@/services/TaskService';
import { Event, TaskStatus } from '@/types/Task';
import TaskStatusBadge from '@/components/TaskStatusBadge';
import ModelBadge from '@/components/ModelBadge';
import EventLog from '@/components/EventLog';
import Header from '@/components/Header';

export default function TaskDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [task, setTask] = useState<Task | null>(null);
  const [events, setEvents] = useState<Event[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);

  const taskId = params.id as string;

  useEffect(() => {
    // Load task and events
    async function loadTaskAndEvents() {
      try {
        const taskData = await taskService.getTask(taskId);
        if (!taskData) {
          // Task not found, redirect to tasks page
          router.push('/tasks');
          return;
        }
        
        setTask(taskData);
        
        const eventsData = await taskService.getTaskEvents(taskId);
        setEvents(eventsData);
      } catch (error) {
        console.error('Error loading task:', error);
      } finally {
        setIsLoading(false);
      }
    }

    loadTaskAndEvents();

    // Start polling for updates if task is running
    const interval = setInterval(async () => {
      const updatedTask = await taskService.getTask(taskId);
      if (updatedTask) {
        setTask(updatedTask);
        
        // If task is running, fetch latest events
        if (updatedTask.status === TaskStatus.RUNNING) {
          const eventsData = await taskService.getTaskEvents(taskId);
          setEvents(eventsData);
        } else {
          // Task is no longer running, stop polling
          if (pollingInterval) {
            clearInterval(pollingInterval);
            setPollingInterval(null);
          }
        }
      }
    }, 5000);

    setPollingInterval(interval);

    // Clean up interval on unmount
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [taskId, router]);

  const handleStartTask = async () => {
    if (!task) return;
    
    try {
      const updatedTask = await taskService.startTask(taskId);
      if (updatedTask) {
        setTask(updatedTask);
      }
    } catch (error) {
      console.error('Error starting task:', error);
    }
  };

  const formatDuration = (milliseconds?: number) => {
    if (!milliseconds) return '-';
    
    const seconds = Math.floor(milliseconds / 1000);
    if (seconds < 60) return `${seconds}s`;
    
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="flex justify-center py-12">
            <div className="text-gray-500">Loading task details...</div>
          </div>
        </main>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="bg-white shadow overflow-hidden sm:rounded-md p-6 text-center">
            <p className="text-gray-500">Task not found.</p>
            <Link 
              href="/tasks"
              className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
            >
              Back to Tasks
            </Link>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 sm:px-0">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">{task.description}</h1>
              <p className="mt-1 text-sm text-gray-700 font-mono">
                Task ID: <span className="font-bold">{task.task_id}</span>
              </p>
            </div>
            <div className="mt-4 sm:mt-0 flex space-x-3">
              <Link
                href="/tasks"
                className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                Back to Tasks
              </Link>
              {task.status === TaskStatus.PENDING && (
                <button
                  onClick={handleStartTask}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
                >
                  Start Task
                </button>
              )}
            </div>
          </div>
        </div>
        
        <div className="mt-6 bg-white shadow-md border border-gray-200 overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6 bg-gray-50 border-b border-gray-200">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Task Details</h3>
          </div>
          <div className="border-t border-gray-200 px-4 py-5 sm:p-0">
            <dl className="sm:divide-y sm:divide-gray-200">
              <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 hover:bg-gray-50">
                <dt className="text-sm font-medium text-gray-900">Status</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  <TaskStatusBadge status={task.status} />
                </dd>
              </div>
              <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 hover:bg-gray-50">
                <dt className="text-sm font-medium text-gray-900">Model</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  <ModelBadge modelInfo={task.model_info} />
                </dd>
              </div>
              <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 hover:bg-gray-50">
                <dt className="text-sm font-medium text-gray-900">Depth</dt>
                <dd className="mt-1 text-sm font-medium text-gray-900 sm:mt-0 sm:col-span-2">{task.depth}</dd>
              </div>
              <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 hover:bg-gray-50">
                <dt className="text-sm font-medium text-gray-900">Max Retries</dt>
                <dd className="mt-1 text-sm font-medium text-gray-900 sm:mt-0 sm:col-span-2">{task.max_retries}</dd>
              </div>
              <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 hover:bg-gray-50">
                <dt className="text-sm font-medium text-gray-900">Created</dt>
                <dd className="mt-1 text-sm font-medium text-gray-900 sm:mt-0 sm:col-span-2">{task.formatted_created}</dd>
              </div>
              {task.started_at && (
                <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 hover:bg-gray-50">
                  <dt className="text-sm font-medium text-gray-900">Started</dt>
                  <dd className="mt-1 text-sm font-medium text-gray-900 sm:mt-0 sm:col-span-2">{task.formatted_started}</dd>
                </div>
              )}
              {task.completed_at && (
                <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 hover:bg-gray-50">
                  <dt className="text-sm font-medium text-gray-900">Completed</dt>
                  <dd className="mt-1 text-sm font-medium text-gray-900 sm:mt-0 sm:col-span-2">{task.formatted_completed}</dd>
                </div>
              )}
              {task.started_at && (
                <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 hover:bg-gray-50">
                  <dt className="text-sm font-medium text-gray-900">Duration</dt>
                  <dd className="mt-1 text-sm font-medium text-gray-900 sm:mt-0 sm:col-span-2">
                    {task.completed_at ? formatDuration(task.duration) : 'Running...'}
                  </dd>
                </div>
              )}
              {task.result && (
                <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 hover:bg-gray-50">
                  <dt className="text-sm font-medium text-gray-900">Result</dt>
                  <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                    <div className="bg-gray-100 p-3 rounded-md border border-gray-300">
                      <pre className="whitespace-pre-wrap text-gray-900">{task.result}</pre>
                    </div>
                  </dd>
                </div>
              )}
              {task.error && (
                <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 hover:bg-gray-50">
                  <dt className="text-sm font-medium text-gray-900">Error</dt>
                  <dd className="mt-1 text-sm text-red-700 font-medium sm:mt-0 sm:col-span-2">
                    <div className="bg-red-50 p-3 rounded-md border border-red-300">
                      {task.error}
                    </div>
                  </dd>
                </div>
              )}
            </dl>
          </div>
        </div>
        
        <div className="mt-8 bg-white shadow-md border border-gray-200 overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6 bg-gray-50 border-b border-gray-200">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Task Events</h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-700">
              Event timeline for this task
            </p>
          </div>
          <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
            <EventLog events={events} />
          </div>
        </div>
      </main>
    </div>
  );
} 