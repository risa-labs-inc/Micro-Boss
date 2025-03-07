"use client";

import { useEffect, useRef } from 'react';
import { LogEvent, LogLevel } from '@/lib/types';

interface LogEntryProps {
  entry: LogEvent;
}

const LogEntry = ({ entry }: LogEntryProps) => {
  // Format the timestamp
  const timeDisplay = entry.formatted_time || 
    new Date(entry.timestamp * 1000).toLocaleTimeString();
  
  // Determine CSS class based on log level
  const getLevelClass = (level: LogLevel) => {
    switch (level) {
      case 'error':
        return 'text-red-600';
      case 'warning':
        return 'text-yellow-600';
      case 'success':
        return 'text-green-600';
      case 'code':
        return 'text-blue-600';
      case 'result':
        return 'text-purple-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className={`log-entry py-1 ${getLevelClass(entry.level)}`}>
      <span className="text-gray-500 mr-2">[{timeDisplay}]</span>
      <span>{entry.message}</span>
    </div>
  );
};

interface LogConsoleProps {
  logs: LogEvent[];
  loading?: boolean;
  maxHeight?: string;
}

const LogConsole = ({ logs = [], loading = false, maxHeight = '500px' }: LogConsoleProps) => {
  const consoleRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new logs are added
  useEffect(() => {
    if (consoleRef.current) {
      consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div 
      ref={consoleRef}
      className="bg-gray-50 border border-gray-200 rounded-md p-4 font-mono text-sm overflow-auto"
      style={{ maxHeight }}
    >
      {loading && logs.length === 0 ? (
        <div className="text-center text-gray-500 py-5">
          <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500 mx-auto mb-3"></div>
          <div>Loading logs...</div>
        </div>
      ) : logs.length === 0 ? (
        <div className="text-center text-gray-500 py-5">
          <div>No logs available yet.</div>
        </div>
      ) : (
        logs.map((log, index) => (
          <LogEntry key={`log-${index}`} entry={log} />
        ))
      )}
    </div>
  );
};

export default LogConsole; 