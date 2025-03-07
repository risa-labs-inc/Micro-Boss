"use client";

import { Task } from '@/lib/types';
import CodeViewer from './CodeViewer';

interface ResultViewerProps {
  result: string | null | undefined;
  task?: Task | null;
  language?: string;
}

const ResultViewer = ({ result, task, language = 'json' }: ResultViewerProps) => {
  if (!result && task) {
    // Show different states based on task status
    if (task.status === 'pending' || task.status === 'running') {
      return (
        <div className="text-center py-10 text-gray-500 border border-dashed border-gray-300 rounded-md">
          {task.status === 'running' ? (
            <>
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto mb-3"></div>
              <p>Task is currently running...</p>
              <p className="mt-1 text-sm">Results will appear here when the task completes.</p>
            </>
          ) : (
            <>
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p>Task is pending execution.</p>
              <p className="mt-1 text-sm">Results will appear here once the task runs and completes.</p>
            </>
          )}
        </div>
      );
    }

    if (task.status === 'failed' && task.error) {
      return (
        <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded overflow-auto max-h-96">
          <h3 className="font-bold mb-2 flex items-center">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Task Failed
          </h3>
          <pre className="text-sm">{task.error}</pre>
        </div>
      );
    }
  }

  if (!result) {
    // No result available
    return (
      <div className="text-center py-10 text-gray-500 border border-dashed border-gray-300 rounded-md">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <p>No result available yet.</p>
      </div>
    );
  }

  // Determine if result is structured or plain text
  let formattedResult = result;
  let detectedLanguage = language;

  // If it looks like JSON but was passed as a string, try to format it
  if (typeof result === 'string' && result.trim().startsWith('{') && detectedLanguage === 'json') {
    try {
      const parsed = JSON.parse(result);
      formattedResult = JSON.stringify(parsed, null, 2);
    } catch (e) {
      // If parsing fails, keep original
      console.warn('Failed to parse result as JSON:', e);
    }
  }

  // Default result view with code syntax highlighting
  return (
    <CodeViewer 
      code={formattedResult} 
      language={detectedLanguage} 
      title="Task Result" 
      showLineNumbers={detectedLanguage !== 'text'}
    />
  );
};

export default ResultViewer; 