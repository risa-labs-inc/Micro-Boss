import Link from 'next/link';

const Footer = () => {
  return (
    <footer className="bg-gray-100 border-t border-gray-200">
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <p className="text-gray-600 text-sm">
              &copy; {new Date().getFullYear()} Microboss. All rights reserved.
            </p>
          </div>
          <div className="flex space-x-4">
            <Link href="/about" className="text-gray-600 hover:text-blue-600 text-sm">
              About
            </Link>
            <Link href="/docs" className="text-gray-600 hover:text-blue-600 text-sm">
              Documentation
            </Link>
            <Link href="/terms" className="text-gray-600 hover:text-blue-600 text-sm">
              Terms
            </Link>
            <Link href="/privacy" className="text-gray-600 hover:text-blue-600 text-sm">
              Privacy
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 