import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import StatusBadge from '../StatusBadge';
import { TaskStatus } from '@/lib/types';

describe('StatusBadge Component', () => {
  it('renders with pending status', () => {
    render(<StatusBadge status="pending" />);
    expect(screen.getByText('Pending')).toBeInTheDocument();
    // Check that it has the correct styling classes for pending
    const badge = screen.getByText('Pending').closest('span');
    expect(badge).toHaveClass('bg-gray-100');
    expect(badge).toHaveClass('text-gray-800');
  });

  it('renders with running status', () => {
    render(<StatusBadge status="running" />);
    expect(screen.getByText('Running')).toBeInTheDocument();
    // Check that it has the correct styling classes for running
    const badge = screen.getByText('Running').closest('span');
    expect(badge).toHaveClass('bg-blue-100');
    expect(badge).toHaveClass('text-blue-800');
  });

  it('renders with completed status', () => {
    render(<StatusBadge status="completed" />);
    expect(screen.getByText('Completed')).toBeInTheDocument();
    // Check that it has the correct styling classes for completed
    const badge = screen.getByText('Completed').closest('span');
    expect(badge).toHaveClass('bg-green-100');
    expect(badge).toHaveClass('text-green-800');
  });

  it('renders with failed status', () => {
    render(<StatusBadge status="failed" />);
    expect(screen.getByText('Failed')).toBeInTheDocument();
    // Check that it has the correct styling classes for failed
    const badge = screen.getByText('Failed').closest('span');
    expect(badge).toHaveClass('bg-red-100');
    expect(badge).toHaveClass('text-red-800');
  });

  it('applies the correct size classes when size is sm', () => {
    render(<StatusBadge status="pending" size="sm" />);
    const badge = screen.getByText('Pending').closest('span');
    expect(badge).toHaveClass('text-xs');
    expect(badge).toHaveClass('px-1.5');
    expect(badge).toHaveClass('py-0.5');
  });

  it('applies the correct size classes when size is md (default)', () => {
    render(<StatusBadge status="pending" />);
    const badge = screen.getByText('Pending').closest('span');
    expect(badge).toHaveClass('text-xs');
    expect(badge).toHaveClass('px-2');
    expect(badge).toHaveClass('py-0.5');
  });

  it('applies the correct size classes when size is lg', () => {
    render(<StatusBadge status="pending" size="lg" />);
    const badge = screen.getByText('Pending').closest('span');
    expect(badge).toHaveClass('text-sm');
    expect(badge).toHaveClass('px-3');
    expect(badge).toHaveClass('py-1');
  });

  it('includes the correct icon for each status', () => {
    const { rerender } = render(<StatusBadge status="pending" />);
    expect(document.querySelector('svg')).toBeInTheDocument();
    
    rerender(<StatusBadge status="running" />);
    const runningIcon = document.querySelector('svg');
    expect(runningIcon).toBeInTheDocument();
    expect(runningIcon).toHaveClass('animate-spin');
    
    rerender(<StatusBadge status="completed" />);
    expect(document.querySelector('svg')).toBeInTheDocument();
    
    rerender(<StatusBadge status="failed" />);
    expect(document.querySelector('svg')).toBeInTheDocument();
  });
}); 