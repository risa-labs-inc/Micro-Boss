"use client";

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import MainLayout from '@/components/layout/MainLayout';
import StatusBadge from '@/components/common/StatusBadge';
import LogConsole from '@/components/task/LogConsole';
import CodeViewer from '@/components/task/CodeViewer';
import Timeline from '@/components/task/Timeline';
import DependencyGraph from '@/components/task/DependencyGraph';
import { Task, LogEvent, GraphData } from '@/lib/types';
import { TaskApi } from '@/lib/services/api';
import useSocketEvents from '@/lib/hooks/useSocketEvents';
import ResultViewer from '@/components/task/ResultViewer';

export default function TaskDetailPage() {
  const params = useParams();
  const taskId = params.taskId as string;

  // State
  const [task, setTask] = useState<Task | null>(null);
  const [logs, setLogs] = useState<LogEvent[]>([]);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<string>('logs');
  const [code, setCode] = useState<string | null>(null);
  const [result, setResult] = useState<string | null>(null);

  // Fetch task data
  useEffect(() => {
    const fetchTaskData = async () => {
      try {
        setLoading(true);
        // Get task details
        const taskData = await TaskApi.getTask(taskId);
        setTask(taskData);

        // Get task logs
        const taskEvents = await TaskApi.getTaskEvents(taskId);
        setLogs(taskEvents);

        // Extract code and result from logs
        taskEvents.forEach((event: LogEvent) => {
          if (event.level === 'code' && event.data?.code) {
            setCode(event.data.code);
          }
          if (event.level === 'result' && event.data?.result) {
            setResult(typeof event.data.result === 'string' ? event.data.result : JSON.stringify(event.data.result, null, 2));
          }
        });

        // Get task graph data
        try {
          const graphData = await TaskApi.getTaskGraph(taskId);
          setGraphData(graphData);
        } catch (err) {
          console.error('Error fetching graph data:', err);
        }
      } catch (err) {
        console.error('Error fetching task data:', err);
      } finally {
        setLoading(false);
      }
    };

    if (taskId) {
      fetchTaskData();
    }
  }, [taskId]);

  // Socket events for real-time updates
  const handleLogEvent = (event: LogEvent) => {
    setLogs(prev => [...prev, event]);

    // Update code if code event
    if (event.level === 'code' && event.data?.code) {
      setCode(event.data.code);
    }

    // Update result if result event
    if (event.level === 'result' && event.data?.result) {
      setResult(typeof event.data.result === 'string' ? event.data.result : JSON.stringify(event.data.result, null, 2));
    }
  };

  useSocketEvents({
    taskId,
    onLogEvent: handleLogEvent,
    onTaskEvent: (event) => {
      // Update task if task data is provided
      if (event.task) {
        setTask(prev => ({ ...prev, ...event.task }));
      }

      // Update graph data if provided
      if (event.graph_data) {
        setGraphData(event.graph_data);
      }
    }
  });

  const handleStartTask = async () => {
    try {
      const response = await TaskApi.startTask(taskId);
      console.log('Task started:', response);
    } catch (err) {
      console.error('Error starting task:', err);
    }
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      </MainLayout>
    );
  }

  if (!task) {
    return (
      <MainLayout>
        <div className="bg-white rounded-lg shadow p-6 text-center">
          <h1 className="text-2xl font-bold text-gray-700 mb-4">Task Not Found</h1>
          <p className="text-gray-600">
            The task with ID '{taskId}' could not be found. It may have been deleted or does not exist.
          </p>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="bg-white shadow rounded-lg overflow-hidden">
        {/* Header and info */}
        <div className="p-6 border-b">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">{task.description}</h1>
              <div className="mt-2 flex items-center">
                <span className="text-gray-600 text-sm mr-4">ID: {task.task_id}</span>
                <StatusBadge status={task.status} size="lg" />
              </div>
              <div className="mt-3 text-sm text-gray-500">
                <div><span className="font-medium">Created:</span> {new Date(task.created_at).toLocaleString()}</div>
                {task.updated_at && (
                  <div><span className="font-medium">Last Updated:</span> {new Date(task.updated_at).toLocaleString()}</div>
                )}
                {task.completed_at && (
                  <div><span className="font-medium">Completed:</span> {new Date(task.completed_at).toLocaleString()}</div>
                )}
              </div>
            </div>
            <div className="flex space-x-2">
              {task.status === 'pending' && (
                <button
                  onClick={handleStartTask}
                  className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded"
                >
                  Start Task
                </button>
              )}
              {task.status === 'running' && (
                <button
                  className="bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded"
                >
                  Cancel Task
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex overflow-x-auto">
            <button
              className={`py-4 px-6 font-medium border-b-2 ${
                activeTab === 'logs'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              onClick={() => setActiveTab('logs')}
            >
              Logs
            </button>
            <button
              className={`py-4 px-6 font-medium border-b-2 ${
                activeTab === 'timeline'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              onClick={() => setActiveTab('timeline')}
            >
              Timeline
            </button>
            <button
              className={`py-4 px-6 font-medium border-b-2 ${
                activeTab === 'visualization'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              onClick={() => setActiveTab('visualization')}
            >
              Visualization
            </button>
            <button
              className={`py-4 px-6 font-medium border-b-2 ${
                activeTab === 'code'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              onClick={() => setActiveTab('code')}
            >
              Code
            </button>
            <button
              className={`py-4 px-6 font-medium border-b-2 ${
                activeTab === 'result'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              onClick={() => setActiveTab('result')}
            >
              Result
            </button>
          </nav>
        </div>

        {/* Tab content */}
        <div className="p-6">
          {activeTab === 'logs' && (
            <div>
              <h2 className="text-lg font-medium text-gray-700 mb-4">Execution Logs</h2>
              <LogConsole logs={logs} loading={loading} maxHeight="600px" />
            </div>
          )}

          {activeTab === 'timeline' && (
            <div>
              <h2 className="text-lg font-medium text-gray-700 mb-4">Execution Timeline</h2>
              <Timeline events={logs} onViewDetails={(event) => {
                if (event.level === 'code') {
                  setActiveTab('code');
                } else if (event.level === 'result') {
                  setActiveTab('result');
                }
              }} />
            </div>
          )}

          {activeTab === 'visualization' && (
            <div>
              <h2 className="text-lg font-medium text-gray-700 mb-4">Task Dependency Graph</h2>
              <DependencyGraph graphData={graphData} height="600px" />
            </div>
          )}

          {activeTab === 'code' && (
            <div>
              <h2 className="text-lg font-medium text-gray-700 mb-4">Generated Code</h2>
              <CodeViewer code={code} language="python" showLineNumbers={true} />
            </div>
          )}

          {activeTab === 'result' && (
            <div>
              <h2 className="text-lg font-medium text-gray-700 mb-4">Task Result</h2>
              <ResultViewer result={result} task={task} />
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
} 