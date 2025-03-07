import Link from 'next/link';
import { useState } from 'react';

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(prev => !prev);
  };

  return (
    <header className="bg-gray-800 text-white shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          {/* Logo and brand */}
          <div className="flex items-center">
            <Link href="/" className="text-xl font-bold text-white flex items-center">
              <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span>Microboss</span>
            </Link>
          </div>

          {/* Desktop navigation */}
          <nav className="hidden md:flex space-x-6">
            <Link href="/" className="hover:text-blue-300 transition">Dashboard</Link>
            <Link href="/tasks" className="hover:text-blue-300 transition">Tasks</Link>
            <Link href="/settings" className="hover:text-blue-300 transition">Settings</Link>
          </nav>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              className="text-white focus:outline-none"
              onClick={toggleMenu}
              aria-label="Toggle menu"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg">
                {isMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile navigation */}
        {isMenuOpen && (
          <nav className="md:hidden pb-4 space-y-3">
            <Link href="/" 
              className="block hover:text-blue-300 transition py-2"
              onClick={() => setIsMenuOpen(false)}>
              Dashboard
            </Link>
            <Link href="/tasks" 
              className="block hover:text-blue-300 transition py-2"
              onClick={() => setIsMenuOpen(false)}>
              Tasks
            </Link>
            <Link href="/settings" 
              className="block hover:text-blue-300 transition py-2"
              onClick={() => setIsMenuOpen(false)}>
              Settings
            </Link>
          </nav>
        )}
      </div>
    </header>
  );
};

export default Header; 