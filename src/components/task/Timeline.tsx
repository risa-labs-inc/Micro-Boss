"use client";

import { useMemo } from 'react';
import { LogEvent, LogLevel } from '@/lib/types';

interface TimelineItemProps {
  event: LogEvent;
  isLast: boolean;
  onViewDetails?: (event: LogEvent) => void;
}

const TimelineItem = ({ event, isLast, onViewDetails }: TimelineItemProps) => {
  // Format the timestamp
  const timeDisplay = event.formatted_time || 
    new Date(event.timestamp * 1000).toLocaleTimeString();
  
  // Determine icon and color based on log level
  const getIconAndColor = (level: LogLevel): { icon: string, color: string } => {
    switch (level) {
      case 'error':
        return { icon: 'M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z', color: 'text-red-500 bg-red-100' };
      case 'warning':
        return { icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z', color: 'text-yellow-500 bg-yellow-100' };
      case 'success':
        return { icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z', color: 'text-green-500 bg-green-100' };
      case 'code':
        return { icon: 'M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4', color: 'text-blue-500 bg-blue-100' };
      case 'result':
        return { icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2', color: 'text-purple-500 bg-purple-100' };
      default:
        return { icon: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z', color: 'text-gray-500 bg-gray-100' };
    }
  };

  const { icon, color } = getIconAndColor(event.level);

  return (
    <div className={`flex ${!isLast ? 'pb-8' : ''}`}>
      <div className="flex flex-col items-center">
        <div className={`rounded-full h-8 w-8 flex items-center justify-center ${color}`}>
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={icon} />
          </svg>
        </div>
        {!isLast && <div className="w-px bg-gray-300 h-full" />}
      </div>
      
      <div className="ml-4 flex-1">
        <div className="flex justify-between items-start mb-1">
          <h4 className="text-sm font-medium text-gray-900">{event.message}</h4>
          <span className="text-xs text-gray-500">{timeDisplay}</span>
        </div>
        
        {/* Show code preview if available */}
        {event.level === 'code' && event.data?.code && (
          <div className="mt-2 p-2 bg-gray-50 rounded-md text-xs font-mono overflow-hidden max-h-20 text-gray-700">
            {event.data.code.split('\n').slice(0, 3).join('\n')}
            {event.data.code.split('\n').length > 3 && '...'}
          </div>
        )}
        
        {/* Show result preview if available */}
        {event.level === 'result' && event.data?.result && (
          <div className="mt-2 p-2 bg-gray-50 rounded-md text-xs font-mono text-gray-700">
            {String(event.data.result).substring(0, 100)}
            {String(event.data.result).length > 100 && '...'}
          </div>
        )}
        
        {/* Add 'View Details' button if there's extra content and a handler */}
        {onViewDetails && (event.level === 'code' || event.level === 'result') && (
          <button 
            onClick={() => onViewDetails(event)}
            className="mt-1 text-xs text-blue-600 hover:text-blue-800 focus:outline-none"
          >
            View Details
          </button>
        )}
      </div>
    </div>
  );
};

interface TimelineProps {
  events: LogEvent[];
  maxItems?: number;
  onViewDetails?: (event: LogEvent) => void;
}

const Timeline = ({ events, maxItems, onViewDetails }: TimelineProps) => {
  // We might want to show only the most recent events if maxItems is set
  const displayEvents = useMemo(() => {
    return maxItems ? [...events].slice(-maxItems) : events;
  }, [events, maxItems]);

  if (!displayEvents || displayEvents.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No timeline events available yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {displayEvents.map((event, index) => (
        <TimelineItem 
          key={`timeline-${event.timestamp}-${index}`} 
          event={event} 
          isLast={index === displayEvents.length - 1}
          onViewDetails={onViewDetails}
        />
      ))}
    </div>
  );
};

export default Timeline; 