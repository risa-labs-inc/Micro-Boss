'use client';

import { Event, EventLevel } from '@/types/Task';
import CodeDisplay from './CodeDisplay';

interface EventLogProps {
  events: Event[];
}

export default function EventLog({ events }: EventLogProps) {
  const getEventIcon = (level: string) => {
    switch (level) {
      case EventLevel.INFO:
        return <span className="text-blue-500 text-xl">ℹ️</span>;
      case EventLevel.SUCCESS:
        return <span className="text-green-500 text-xl">✅</span>;
      case EventLevel.WARNING:
        return <span className="text-yellow-500 text-xl">⚠️</span>;
      case EventLevel.ERROR:
        return <span className="text-red-500 text-xl">❌</span>;
      case EventLevel.CODE:
        return <span className="text-purple-500 text-xl">💻</span>;
      case EventLevel.RESULT:
        return <span className="text-green-500 text-xl">🏁</span>;
      default:
        return <span className="text-gray-500 text-xl">•</span>;
    }
  };

  const renderEventContent = (event: Event) => {
    if (event.level === EventLevel.CODE && event.data?.code) {
      return (
        <div className="mt-2">
          <CodeDisplay code={event.data.code} language={event.data.language || 'python'} />
        </div>
      );
    }

    if (event.level === EventLevel.RESULT && event.data?.result) {
      return (
        <div className="mt-2 p-4 bg-gray-100 border border-gray-300 rounded-md">
          <h4 className="text-sm font-semibold mb-2 text-gray-900">Result:</h4>
          <pre className="whitespace-pre-wrap text-sm text-gray-900">{event.data.result}</pre>
        </div>
      );
    }

    return null;
  };

  const getEventClasses = (level: string) => {
    switch (level) {
      case EventLevel.INFO:
        return 'border-blue-300 bg-blue-50';
      case EventLevel.SUCCESS:
        return 'border-green-300 bg-green-50';
      case EventLevel.WARNING:
        return 'border-yellow-300 bg-yellow-50';
      case EventLevel.ERROR:
        return 'border-red-300 bg-red-50';
      case EventLevel.CODE:
        return 'border-purple-300 bg-purple-50';
      case EventLevel.RESULT:
        return 'border-green-300 bg-green-50';
      default:
        return 'border-gray-300 bg-gray-50';
    }
  };

  return (
    <div className="space-y-4">
      {events.length === 0 ? (
        <div className="text-center py-8 text-gray-600 font-medium">No events yet</div>
      ) : (
        events.map((event) => (
          <div 
            key={event.id}
            className={`p-4 rounded-md border-2 shadow-sm ${getEventClasses(event.level)}`}
          >
            <div className="flex items-start">
              <div className="mr-3 mt-0.5">{getEventIcon(event.level)}</div>
              <div className="flex-1">
                <div className="flex justify-between items-start">
                  <div className="font-medium text-gray-900">{event.message}</div>
                  <div className="text-sm text-gray-700 ml-2 font-mono bg-gray-100 px-2 py-0.5 rounded">{event.formatted_time}</div>
                </div>
                {renderEventContent(event)}
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
} 