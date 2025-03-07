'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import taskService from '@/services/TaskService';
import { Task } from '@/services/TaskService';
import { TaskStatus } from '@/types/Task';
import TaskStatusBadge from '@/components/TaskStatusBadge';
import ModelBadge from '@/components/ModelBadge';
import Header from '@/components/Header';

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadTasks() {
      try {
        const tasks = await taskService.getTasks();
        setTasks(tasks);
      } catch (error) {
        console.error('Error loading tasks:', error);
      } finally {
        setIsLoading(false);
      }
    }

    loadTasks();
  }, []);

  const handleStartTask = async (taskId: string) => {
    try {
      const updatedTask = await taskService.startTask(taskId);
      if (updatedTask) {
        setTasks(prevTasks => 
          prevTasks.map(task => 
            task.task_id === taskId ? updatedTask : task
          )
        );
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

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 sm:px-0">
          <h1 className="text-2xl font-semibold text-gray-900">Tasks</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage and track your distributed tasks
          </p>
        </div>
        
        <div className="mt-6">
          {isLoading ? (
            <div className="flex justify-center py-8">
              <div className="text-gray-500">Loading tasks...</div>
            </div>
          ) : tasks.length === 0 ? (
            <div className="bg-white shadow overflow-hidden sm:rounded-md p-6 text-center">
              <p className="text-gray-500">No tasks found. Create a new task to get started.</p>
              <Link 
                href="/tasks/new"
                className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
              >
                Create New Task
              </Link>
            </div>
          ) : (
            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <ul className="divide-y divide-gray-200">
                {tasks.map((task) => (
                  <li key={task.task_id}>
                    <div className="px-4 py-4 sm:px-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <Link href={`/tasks/${task.task_id}`} className="text-blue-600 font-medium hover:text-blue-800">
                            {task.description}
                          </Link>
                        </div>
                        <div className="flex space-x-2">
                          <ModelBadge modelInfo={task.model_info} />
                          <TaskStatusBadge status={task.status} />
                        </div>
                      </div>
                      <div className="mt-2 sm:flex sm:justify-between">
                        <div className="sm:flex sm:space-x-4">
                          <div className="flex items-center text-sm text-gray-500">
                            <span className="mr-1">ID:</span>
                            <span className="font-mono">{task.task_id.substring(0, 8)}</span>
                          </div>
                          <div className="flex items-center text-sm text-gray-500 mt-1 sm:mt-0">
                            <span className="mr-1">Depth:</span>
                            {task.depth}
                          </div>
                        </div>
                        <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                          <div className="flex space-x-4">
                            <div>
                              <span className="mr-1">Created:</span>
                              {task.formatted_created}
                            </div>
                            {task.started_at && (
                              <div>
                                <span className="mr-1">Duration:</span>
                                {task.completed_at 
                                  ? formatDuration(task.duration) 
                                  : 'Running...'}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="mt-2 flex justify-end">
                        <Link 
                          href={`/tasks/${task.task_id}`}
                          className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200"
                        >
                          View Details
                        </Link>
                        {task.status === TaskStatus.PENDING && (
                          <button
                            onClick={() => handleStartTask(task.task_id)}
                            className="ml-3 inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-green-700 bg-green-100 hover:bg-green-200"
                          >
                            Start Task
                          </button>
                        )}
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </main>
    </div>
  );
} 