import React from 'react';

const Button = ({ onClick, children, variant = 'primary' }) => {
  const getVariantClasses = () => {
    switch (variant) {
      case 'primary':
        return 'bg-blue-500 hover:bg-blue-600 text-white';
      case 'secondary':
        return 'bg-gray-500 hover:bg-gray-600 text-white';
      case 'success':
        return 'bg-green-500 hover:bg-green-600 text-white';
      case 'danger':
        return 'bg-red-500 hover:bg-red-600 text-white';
      default:
        return 'bg-blue-500 hover:bg-blue-600 text-white';
    }
  };

  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded font-semibold ${getVariantClasses()}`}
      data-testid="button"
    >
      {children}
    </button>
  );
};

export default Button; 