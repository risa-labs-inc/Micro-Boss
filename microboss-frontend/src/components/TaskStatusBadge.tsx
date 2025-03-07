import { TaskStatus } from '@/types/Task';

interface TaskStatusBadgeProps {
  status: TaskStatus;
}

export default function TaskStatusBadge({ status }: TaskStatusBadgeProps) {
  const getStatusClasses = () => {
    switch (status) {
      case TaskStatus.PENDING:
        return 'bg-gray-400 text-gray-900';
      case TaskStatus.RUNNING:
        return 'bg-blue-500 text-white';
      case TaskStatus.COMPLETED:
        return 'bg-green-500 text-white';
      case TaskStatus.FAILED:
        return 'bg-red-500 text-white';
      default:
        return 'bg-gray-400 text-gray-900';
    }
  };

  const getStatusText = () => {
    return status.charAt(0).toUpperCase() + status.slice(1);
  };

  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusClasses()}`}>
      {getStatusText()}
    </span>
  );
} 