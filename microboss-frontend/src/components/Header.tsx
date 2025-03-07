'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Header() {
  const pathname = usePathname();

  const isActive = (path: string) => {
    return pathname === path ? 'text-blue-500 border-b-2 border-blue-500' : 'text-gray-600 hover:text-gray-900';
  };

  return (
    <header className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link href="/" className="text-2xl font-bold text-blue-600">
                Microboss
              </Link>
            </div>
            <nav className="ml-10 flex space-x-8">
              <Link href="/tasks" className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/tasks')}`}>
                Tasks
              </Link>
              <Link href="/models" className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/models')}`}>
                Models
              </Link>
              <Link href="/settings" className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${isActive('/settings')}`}>
                Settings
              </Link>
            </nav>
          </div>
          <div className="flex items-center">
            <Link
              href="/tasks/new"
              className="ml-3 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              New Task
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
} 