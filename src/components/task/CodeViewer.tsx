"use client";

import { useEffect, useRef } from 'react';
import hljs from 'highlight.js';
import 'highlight.js/styles/github.css';

interface CodeViewerProps {
  code: string | null | undefined;
  language?: string;
  title?: string;
  showLineNumbers?: boolean;
}

const CodeViewer = ({ 
  code, 
  language = 'python', 
  title = 'Generated Code',
  showLineNumbers = true
}: CodeViewerProps) => {
  const codeRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (codeRef.current && code) {
      hljs.highlightElement(codeRef.current);
    }
  }, [code]);

  // Handle line numbers if enabled
  const renderCode = () => {
    if (!code) return null;
    
    if (showLineNumbers) {
      const lines = code.split('\n');
      return (
        <table className="w-full">
          <tbody>
            {lines.map((line, i) => (
              <tr key={i} className="leading-relaxed">
                <td className="text-right pr-4 text-gray-400 select-none w-12">{i + 1}</td>
                <td className="whitespace-pre">{line}</td>
              </tr>
            ))}
          </tbody>
        </table>
      );
    }
    
    return code;
  };

  if (!code) {
    return (
      <div className="text-center py-8 text-gray-500">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        <p className="mt-2">No code has been generated yet.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-md shadow-sm">
      {title && (
        <div className="border-b px-4 py-3 flex justify-between items-center">
          <h3 className="font-medium text-gray-700">{title}</h3>
          <div className="flex space-x-2">
            <button 
              onClick={() => navigator.clipboard.writeText(code)}
              className="text-gray-500 hover:text-gray-700 focus:outline-none"
              title="Copy to clipboard"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
              </svg>
            </button>
          </div>
        </div>
      )}
      <div className="overflow-x-auto">
        <pre className="p-4 m-0 text-sm bg-gray-50 rounded-b-md">
          {showLineNumbers ? (
            renderCode()
          ) : (
            <code ref={codeRef} className={`language-${language}`}>
              {code}
            </code>
          )}
        </pre>
      </div>
    </div>
  );
};

export default CodeViewer; 