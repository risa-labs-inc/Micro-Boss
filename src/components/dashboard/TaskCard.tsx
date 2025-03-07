"use client";

import Link from 'next/link';
import { Task } from '@/lib/types';
import StatusBadge from '@/components/common/StatusBadge';

interface TaskCardProps {
  task: Task;
  onStart?: (taskId: string) => void;
  onCancel?: (taskId: string) => void;
}

const TaskCard = ({ task, onStart, onCancel }: TaskCardProps) => {
  const getTimeDisplay = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
      <div className="p-4">
        <div className="flex justify-between items-start mb-2">
          <Link href={`/tasks/${task.task_id}`} className="text-lg font-medium text-blue-600 hover:text-blue-800 hover:underline truncate max-w-xs">
            {task.description}
          </Link>
          <StatusBadge status={task.status} />
        </div>
        
        <div className="mb-3 text-sm text-gray-500">
          <div className="flex justify-between">
            <span>ID: {task.task_id}</span>
            <span className="font-medium">
              {task.status === 'running' && (
                <span className="flex items-center text-blue-600">
                  <svg className="w-3 h-3 mr-1 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  In Progress
                </span>
              )}
            </span>
          </div>
        </div>
        
        <div className="flex flex-col space-y-1 text-xs text-gray-500 mb-4">
          <div className="flex justify-between">
            <span>Created:</span>
            <span>{getTimeDisplay(task.created_at)}</span>
          </div>
          {task.updated_at && (
            <div className="flex justify-between">
              <span>Last Updated:</span>
              <span>{getTimeDisplay(task.updated_at)}</span>
            </div>
          )}
          {task.completed_at && (
            <div className="flex justify-between">
              <span>Completed:</span>
              <span>{getTimeDisplay(task.completed_at)}</span>
            </div>
          )}
        </div>
        
        {/* Task result summary if available */}
        {task.status === 'completed' && task.result && (
          <div className="mb-4 text-sm">
            <h4 className="font-medium text-gray-700 mb-1">Result:</h4>
            <div className="bg-gray-50 p-2 rounded text-xs font-mono text-gray-800 overflow-hidden max-h-16">
              {typeof task.result === 'string' 
                ? task.result.substring(0, 100) + (task.result.length > 100 ? '...' : '')
                : JSON.stringify(task.result).substring(0, 100) + '...'}
            </div>
          </div>
        )}
        
        {/* Error message if failed */}
        {task.status === 'failed' && task.error && (
          <div className="mb-4 text-sm">
            <h4 className="font-medium text-red-600 mb-1">Error:</h4>
            <div className="bg-red-50 p-2 rounded text-xs font-mono text-red-700 overflow-hidden max-h-16">
              {task.error.substring(0, 100) + (task.error.length > 100 ? '...' : '')}
            </div>
          </div>
        )}
        
        {/* Action buttons */}
        <div className="flex justify-end space-x-2 mt-2">
          {task.status === 'pending' && onStart && (
            <button 
              onClick={() => onStart(task.task_id)}
              className="text-xs py-1 px-3 bg-blue-600 hover:bg-blue-700 text-white rounded-md"
            >
              Start
            </button>
          )}
          
          {task.status === 'running' && onCancel && (
            <button 
              onClick={() => onCancel(task.task_id)}
              className="text-xs py-1 px-3 bg-red-600 hover:bg-red-700 text-white rounded-md"
            >
              Cancel
            </button>
          )}
          
          <Link
            href={`/tasks/${task.task_id}`}
            className="text-xs py-1 px-3 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-md"
          >
            View Details
          </Link>
        </div>
      </div>
    </div>
  );
};

export default TaskCard; 