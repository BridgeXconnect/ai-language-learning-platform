import React from 'react';
import { clsx } from 'clsx';

const LoadingSpinner = ({ 
  size = 'md', 
  color = 'primary', 
  className = '',
  label = 'Loading...'
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12',
  };

  const colorClasses = {
    primary: 'border-gray-300 border-t-primary-600',
    white: 'border-gray-200 border-t-white',
    gray: 'border-gray-200 border-t-gray-600',
    success: 'border-gray-300 border-t-success-600',
    warning: 'border-gray-300 border-t-warning-600',
    error: 'border-gray-300 border-t-error-600',
  };

  return (
    <div className={clsx('flex items-center justify-center', className)} role="status" aria-label={label}>
      <div
        className={clsx(
          'loading-spinner border-2 rounded-full',
          sizeClasses[size],
          colorClasses[color]
        )}
      />
      <span className="sr-only">{label}</span>
    </div>
  );
};

export default LoadingSpinner;