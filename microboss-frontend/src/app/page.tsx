import Link from 'next/link';
import Header from '@/components/Header';

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-grow flex flex-col items-center justify-center bg-gradient-to-b from-gray-900 to-gray-800 text-white py-12">
        <div className="max-w-3xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl sm:text-5xl font-bold mb-6">Microboss</h1>
          <p className="text-xl mb-10">A robust task management platform for distributed systems</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
            <div className="bg-gray-800 bg-opacity-70 p-6 rounded-lg shadow-md">
              <h3 className="text-xl font-semibold mb-3">Task Management</h3>
              <p className="mb-4">Create, monitor, and manage distributed tasks with ease</p>
              <Link 
                href="/tasks" 
                className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-gray-900 bg-white hover:bg-gray-100"
              >
                View Tasks
              </Link>
            </div>
            <div className="bg-gray-800 bg-opacity-70 p-6 rounded-lg shadow-md">
              <h3 className="text-xl font-semibold mb-3">Create New Task</h3>
              <p className="mb-4">Quickly start a new distributed computation task</p>
              <Link 
                href="/tasks/new" 
                className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                New Task
              </Link>
            </div>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
            <div className="bg-gray-800 bg-opacity-50 p-4 rounded-lg shadow-sm">
              <h4 className="font-semibold mb-2">Real-time Updates</h4>
              <p className="text-sm">Get instant notifications and live status updates</p>
            </div>
            <div className="bg-gray-800 bg-opacity-50 p-4 rounded-lg shadow-sm">
              <h4 className="font-semibold mb-2">Performance Analytics</h4>
              <p className="text-sm">Visualize system performance and resource utilization</p>
            </div>
            <div className="bg-gray-800 bg-opacity-50 p-4 rounded-lg shadow-sm">
              <h4 className="font-semibold mb-2">AI-Powered</h4>
              <p className="text-sm">Leverage state-of-the-art AI models for complex tasks</p>
            </div>
          </div>
        </div>
      </main>
      
      <footer className="bg-gray-900 text-gray-400 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row justify-between items-center">
            <div className="mb-4 sm:mb-0">
              <p>&copy; {new Date().getFullYear()} Microboss. All rights reserved.</p>
            </div>
            <div className="flex space-x-6">
              <a href="#" className="text-gray-400 hover:text-white">Documentation</a>
              <a href="#" className="text-gray-400 hover:text-white">API</a>
              <a href="#" className="text-gray-400 hover:text-white">GitHub</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
