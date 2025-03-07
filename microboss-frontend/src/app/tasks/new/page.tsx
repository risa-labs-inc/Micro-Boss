'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import taskService from '@/services/TaskService';
import Header from '@/components/Header';

// Mock available models
const availableModels = {
  'Anthropic': ['claude-3-7-sonnet-20250219', 'claude-3-5-sonnet-20240620', 'claude-3-opus-20240229'],
  'OpenAI': ['gpt-4o-2024-05-13', 'gpt-4-turbo', 'gpt-4']
};

export default function NewTaskPage() {
  const router = useRouter();
  const [description, setDescription] = useState('');
  const [depth, setDepth] = useState(1);
  const [maxRetries, setMaxRetries] = useState(3);
  const [maxDecompositionDepth, setMaxDecompositionDepth] = useState(10);
  const [selectedModel, setSelectedModel] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!description) {
      setError('Task description is required');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const task = await taskService.createTask(
        description,
        depth,
        maxRetries,
        maxDecompositionDepth,
        selectedModel
      );

      // Start the task immediately
      await taskService.startTask(task.task_id);
      
      // Redirect to task detail page
      router.push(`/tasks/${task.task_id}`);
    } catch (error) {
      console.error('Error creating task:', error);
      setError('An error occurred while creating the task. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 sm:px-0">
          <h1 className="text-2xl font-semibold text-gray-900">Create New Task</h1>
          <p className="mt-1 text-sm text-gray-600">
            Create a new task to solve with Microboss
          </p>
        </div>
        
        <div className="mt-6 bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            {error && (
              <div className="mb-4 p-4 bg-red-50 border-l-4 border-red-500 text-red-700">
                <p>{error}</p>
              </div>
            )}
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-900">
                  Task Description
                </label>
                <div className="mt-1">
                  <textarea
                    id="description"
                    name="description"
                    rows={3}
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className="shadow-sm border-2 border-gray-300 focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm rounded-md p-2 text-gray-900"
                    placeholder="Describe the task you want Microboss to solve. Be as specific as possible."
                    required
                  />
                </div>
                <p className="mt-2 text-sm text-gray-700">
                  Example: "Calculate factorial of 10" or "Find prime numbers between 1 and 100"
                </p>
              </div>
              
              <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-3">
                <div>
                  <label htmlFor="depth" className="block text-sm font-medium text-gray-900">
                    Depth
                  </label>
                  <div className="mt-1">
                    <input
                      type="number"
                      name="depth"
                      id="depth"
                      min={1}
                      max={5}
                      value={depth}
                      onChange={(e) => setDepth(parseInt(e.target.value))}
                      className="shadow-sm border-2 border-gray-300 focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm rounded-md p-2 text-gray-900"
                    />
                  </div>
                  <p className="mt-2 text-xs text-gray-700">
                    Depth of task decomposition (1-5)
                  </p>
                </div>
                
                <div>
                  <label htmlFor="maxRetries" className="block text-sm font-medium text-gray-900">
                    Max Retries
                  </label>
                  <div className="mt-1">
                    <input
                      type="number"
                      name="maxRetries"
                      id="maxRetries"
                      min={0}
                      max={10}
                      value={maxRetries}
                      onChange={(e) => setMaxRetries(parseInt(e.target.value))}
                      className="shadow-sm border-2 border-gray-300 focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm rounded-md p-2 text-gray-900"
                    />
                  </div>
                  <p className="mt-2 text-xs text-gray-700">
                    Maximum number of retries (0-10)
                  </p>
                </div>
                
                <div>
                  <label htmlFor="maxDecompositionDepth" className="block text-sm font-medium text-gray-900">
                    Max Decomposition Depth
                  </label>
                  <div className="mt-1">
                    <input
                      type="number"
                      name="maxDecompositionDepth"
                      id="maxDecompositionDepth"
                      min={1}
                      max={20}
                      value={maxDecompositionDepth}
                      onChange={(e) => setMaxDecompositionDepth(parseInt(e.target.value))}
                      className="shadow-sm border-2 border-gray-300 focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm rounded-md p-2 text-gray-900"
                    />
                  </div>
                  <p className="mt-2 text-xs text-gray-700">
                    Maximum levels of subtask decomposition (1-20)
                  </p>
                </div>
              </div>
              
              <div>
                <label htmlFor="selectedModel" className="block text-sm font-medium text-gray-900">
                  AI Model
                </label>
                <div className="mt-1">
                  <select
                    id="selectedModel"
                    name="selectedModel"
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="shadow-sm border-2 border-gray-300 focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm rounded-md p-2 text-gray-900"
                  >
                    <option value="">Default</option>
                    {Object.entries(availableModels).map(([provider, models]) => (
                      <optgroup key={provider} label={provider}>
                        {models.map(model => (
                          <option key={model} value={model}>
                            {provider} - {model}
                          </option>
                        ))}
                      </optgroup>
                    ))}
                  </select>
                </div>
                <p className="mt-2 text-sm text-gray-700">
                  Select the AI model to use for this task
                </p>
              </div>
              
              <div className="flex justify-end space-x-3">
                <Link
                  href="/tasks"
                  className="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
                  Cancel
                </Link>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? 'Creating...' : 'Create and Run Task'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
} 