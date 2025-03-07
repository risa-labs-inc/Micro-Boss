'use client';

interface CodeDisplayProps {
  code: string;
  language?: string;
}

export default function CodeDisplay({ code, language = 'python' }: CodeDisplayProps) {
  return (
    <div className="my-4 overflow-hidden rounded-md shadow-md border border-gray-300">
      <div className="bg-gray-800 px-4 py-2 text-sm text-gray-200 flex justify-between items-center">
        <div className="font-medium">
          {language.charAt(0).toUpperCase() + language.slice(1)}
        </div>
        <button 
          onClick={() => navigator.clipboard.writeText(code)}
          className="bg-gray-700 hover:bg-gray-600 text-gray-200 px-3 py-1 rounded text-xs font-medium"
        >
          Copy Code
        </button>
      </div>
      <pre className="bg-gray-900 p-4 text-white overflow-auto text-sm leading-relaxed">
        <code>{code}</code>
      </pre>
    </div>
  );
} 