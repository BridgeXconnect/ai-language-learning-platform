import React from 'react';
import { motion } from 'framer-motion';
import { Loader2, FileText, Upload, Brain, Zap } from 'lucide-react';
import { 
  ArrowPathIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  SparklesIcon,
  ClockIcon,
  DocumentTextIcon,
  UserGroupIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

// Basic loading spinner
export const LoadingSpinner = ({ size = 'md', className = '', message = 'Loading...', submessage = null, color = 'primary' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };

  const colorClasses = {
    primary: 'border-primary-600',
    success: 'border-success-600',
    warning: 'border-warning-600',
    error: 'border-error-600'
  };

  return (
    <div className={`flex flex-col items-center justify-center space-y-3 ${className}`}>
      <div className={`${sizeClasses[size]} border-2 border-neutral-200 border-t-${color}-600 rounded-full animate-spin`} />
      {message && (
        <div className="text-center">
          <p className="body-sm font-medium text-neutral-700">{message}</p>
          {submessage && (
            <p className="body-xs text-neutral-500 mt-1">{submessage}</p>
          )}
        </div>
      )}
    </div>
  );
};

// Loading button state
export const LoadingButton = ({ 
  loading, 
  children, 
  loadingText = 'Loading...', 
  disabled,
  className = '',
  variant = 'primary',
  size = 'md',
  icon: Icon = null,
  ...props 
}) => {
  const baseClasses = `btn btn-${variant} btn-${size}`;
  const loadingClasses = loading ? 'btn-loading' : '';
  
  return (
    <button
      disabled={disabled || loading}
      className={`${baseClasses} ${loadingClasses} ${className}`}
      {...props}
    >
      {!loading && Icon && <Icon className="h-4 w-4" />}
      {loading ? loadingText : children}
    </button>
  );
};

// Page loading skeleton
export const PageLoadingSkeleton = ({ type = 'dashboard' }) => {
  const renderDashboardSkeleton = () => (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header Skeleton */}
      <div className="bg-white rounded-xl p-6 shadow-base">
        <div className="flex items-center justify-between mb-4">
          <div className="space-y-2">
            <div className="skeleton skeleton-text h-8 w-64" />
            <div className="skeleton skeleton-text h-4 w-96" />
          </div>
          <div className="flex space-x-3">
            <div className="skeleton skeleton-button" />
            <div className="skeleton skeleton-button" />
          </div>
        </div>
      </div>

      {/* Stats Cards Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="card">
            <div className="card-body">
              <div className="flex items-center justify-between">
                <div className="space-y-2 flex-1">
                  <div className="skeleton skeleton-text h-4 w-24" />
                  <div className="skeleton skeleton-text h-8 w-16" />
                  <div className="skeleton skeleton-text h-3 w-20" />
                </div>
                <div className="skeleton w-12 h-12 rounded-lg" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Main Content Skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="card">
              <div className="card-header">
                <div className="skeleton skeleton-text h-6 w-48" />
              </div>
              <div className="card-body space-y-4">
                <div className="skeleton skeleton-text h-4 w-full" />
                <div className="skeleton skeleton-text h-4 w-3/4" />
                <div className="skeleton skeleton-text h-4 w-1/2" />
              </div>
            </div>
          ))}
        </div>
        
        <div className="space-y-6">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="card">
              <div className="card-header">
                <div className="skeleton skeleton-text h-5 w-32" />
              </div>
              <div className="card-body space-y-3">
                {[...Array(4)].map((_, j) => (
                  <div key={j} className="skeleton skeleton-text h-4 w-full" />
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderLessonSkeleton = () => (
    <div className="container mx-auto py-6 space-y-6">
      {/* Video Player Skeleton */}
      <div className="skeleton w-full aspect-video rounded-xl" />
      
      {/* Lesson Content */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-3 space-y-6">
          <div className="card">
            <div className="card-body space-y-4">
              <div className="skeleton skeleton-text h-6 w-3/4" />
              <div className="skeleton skeleton-text h-4 w-full" />
              <div className="skeleton skeleton-text h-4 w-5/6" />
              <div className="skeleton skeleton-text h-4 w-2/3" />
            </div>
          </div>
        </div>
        
        <div className="space-y-4">
          <div className="card">
            <div className="card-body space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="skeleton skeleton-text h-4 w-full" />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const skeletonTypes = {
    dashboard: renderDashboardSkeleton,
    lesson: renderLessonSkeleton,
    default: renderDashboardSkeleton
  };

  return (
    <div className="min-h-screen bg-neutral-50 animate-pulse">
      {skeletonTypes[type] || skeletonTypes.default}
    </div>
  );
};

// Card loading skeleton
export const CardLoadingSkeleton = ({ count = 3, variant = 'default' }) => {
  const renderCard = (index) => (
    <div key={index} className="card animate-pulse">
      <div className="card-body">
        <div className="flex items-start space-x-4">
          <div className="skeleton skeleton-avatar" />
          <div className="flex-1 space-y-3">
            <div className="skeleton skeleton-text h-5 w-3/4" />
            <div className="skeleton skeleton-text h-4 w-full" />
            <div className="skeleton skeleton-text h-4 w-5/6" />
            <div className="flex space-x-2 mt-4">
              <div className="skeleton skeleton-button w-20" />
              <div className="skeleton skeleton-button w-16" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-4">
      {[...Array(count)].map((_, i) => renderCard(i))}
    </div>
  );
};

// Table loading skeleton
export const TableLoadingSkeleton = ({ rows = 5, columns = 4 }) => (
  <div className="card animate-pulse">
    <div className="card-header">
      <div className="skeleton skeleton-text h-6 w-48" />
    </div>
    <div className="card-body p-0">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-neutral-50">
            <tr>
              {[...Array(columns)].map((_, i) => (
                <th key={i} className="px-6 py-4">
                  <div className="skeleton skeleton-text h-4 w-24" />
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-200">
            {[...Array(rows)].map((_, i) => (
              <tr key={i}>
                {[...Array(columns)].map((_, j) => (
                  <td key={j} className="px-6 py-4">
                    <div className="skeleton skeleton-text h-4 w-32" />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  </div>
);

// Full page loading with message
export const FullPageLoading = ({ 
  message = 'Loading...', 
  submessage = null,
  type = 'default',
  showProgress = false,
  progress = 0
}) => {
  const getLoadingIcon = () => {
    switch (type) {
      case 'ai': return SparklesIcon;
      case 'processing': return ArrowPathIcon;
      case 'saving': return CheckCircleIcon;
      case 'analyzing': return ChartBarIcon;
      default: return ClockIcon;
    }
  };

  const Icon = getLoadingIcon();

  return (
    <div className="fixed inset-0 bg-neutral-50 flex items-center justify-center z-50">
      <div className="text-center max-w-md mx-auto px-6">
        <div className="mb-8">
          <div className="relative">
            <div className="w-20 h-20 mx-auto mb-6 bg-primary-100 rounded-full flex items-center justify-center">
              <Icon className="h-10 w-10 text-primary-600 animate-pulse" />
            </div>
            <div className="absolute inset-0 w-20 h-20 mx-auto border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
          </div>
        </div>
        
        <div className="space-y-4">
          <h2 className="heading-xl text-neutral-900">{message}</h2>
          {submessage && (
            <p className="body-base text-neutral-600">{submessage}</p>
          )}
          
          {showProgress && (
            <div className="w-full max-w-xs mx-auto">
              <div className="progress">
                <div 
                  className="progress-bar"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="body-xs text-neutral-500 mt-2">{progress}% complete</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Inline loading with message
export const InlineLoading = ({ 
  message = 'Loading...', 
  size = 'md',
  variant = 'default'
}) => {
  return (
    <div className="flex items-center justify-center space-x-3 py-8">
      <LoadingSpinner size={size} />
      <span className="body-sm text-neutral-600">{message}</span>
    </div>
  );
};

// Loading overlay for components
export const LoadingOverlay = ({ 
  loading, 
  children, 
  message = 'Loading...',
  blur = true
}) => {
  if (!loading) return children;

  return (
    <div className="relative">
      <div className={`${blur ? 'filter blur-sm' : 'opacity-50'} pointer-events-none`}>
        {children}
      </div>
      <div className="absolute inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center">
        <LoadingSpinner message={message} />
      </div>
    </div>
  );
};

// AI-specific loading states
export const AIProcessingLoader = ({ 
  stage = 'processing', 
  progress = 0,
  stages = [
    { id: 'analyzing', label: 'Analyzing content', icon: DocumentTextIcon },
    { id: 'generating', label: 'Generating course', icon: SparklesIcon },
    { id: 'optimizing', label: 'Optimizing structure', icon: ChartBarIcon },
    { id: 'finalizing', label: 'Finalizing details', icon: CheckCircleIcon }
  ]
}) => {
  const currentStageIndex = stages.findIndex(s => s.id === stage);

  return (
    <div className="card max-w-md mx-auto">
      <div className="card-body text-center space-y-6">
        <div className="relative">
          <div className="w-16 h-16 mx-auto bg-gradient-primary rounded-full flex items-center justify-center">
            <SparklesIcon className="h-8 w-8 text-white animate-pulse" />
          </div>
          <div className="absolute inset-0 w-16 h-16 mx-auto border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
        </div>

        <div className="space-y-4">
          <h3 className="heading-lg">AI Processing</h3>
          
          <div className="space-y-3">
            {stages.map((stageItem, index) => {
              const Icon = stageItem.icon;
              const isActive = index === currentStageIndex;
              const isCompleted = index < currentStageIndex;
              
              return (
                <div 
                  key={stageItem.id}
                  className={`flex items-center space-x-3 p-3 rounded-lg transition-all ${
                    isActive ? 'bg-primary-50 border border-primary-200' :
                    isCompleted ? 'bg-success-50' : 'bg-neutral-50'
                  }`}
                >
                  <div className={`p-2 rounded-full ${
                    isActive ? 'bg-primary-100 text-primary-600' :
                    isCompleted ? 'bg-success-100 text-success-600' :
                    'bg-neutral-200 text-neutral-400'
                  }`}>
                    <Icon className="h-4 w-4" />
                  </div>
                  <span className={`body-sm font-medium ${
                    isActive ? 'text-primary-700' :
                    isCompleted ? 'text-success-700' :
                    'text-neutral-500'
                  }`}>
                    {stageItem.label}
                  </span>
                  {isActive && (
                    <div className="ml-auto">
                      <div className="loading-spinner-sm" />
                    </div>
                  )}
                  {isCompleted && (
                    <div className="ml-auto">
                      <CheckCircleIcon className="h-4 w-4 text-success-600" />
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <div className="progress">
            <div 
              className="progress-bar"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="body-xs text-neutral-500">{progress}% complete</p>
        </div>
      </div>
    </div>
  );
};

// Shimmer effect for content loading
export const ShimmerLoader = ({ className = 'h-4 bg-gray-200 rounded' }) => {
  return (
    <div className={`animate-pulse ${className}`}>
      <div className="shimmer-effect"></div>
    </div>
  );
};

// Progressive loading for images
export const ProgressiveImage = ({ 
  src, 
  alt, 
  className = '', 
  placeholder = null,
  fallback = null
}) => {
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(false);

  const handleLoad = () => setLoading(false);
  const handleError = () => {
    setLoading(false);
    setError(true);
  };

  if (error && fallback) {
    return fallback;
  }

  return (
    <div className={`relative overflow-hidden ${className}`}>
      {loading && (
        <div className="absolute inset-0 bg-neutral-200 animate-pulse flex items-center justify-center">
          {placeholder || <div className="skeleton w-full h-full" />}
        </div>
      )}
      <img
        src={src}
        alt={alt}
        onLoad={handleLoad}
        onError={handleError}
        className={`transition-opacity duration-300 ${
          loading ? 'opacity-0' : 'opacity-100'
        } ${className}`}
      />
    </div>
  );
};

// Dots loading animation
export const DotsLoader = ({ size = 'md', color = 'blue' }) => {
  const sizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4'
  };

  const colorClasses = {
    blue: 'bg-blue-600',
    gray: 'bg-gray-600',
    green: 'bg-green-600',
    red: 'bg-red-600'
  };

  return (
    <div className="flex space-x-1">
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className={`${sizeClasses[size]} ${colorClasses[color]} rounded-full`}
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.7, 1, 0.7]
          }}
          transition={{
            duration: 0.8,
            repeat: Infinity,
            delay: i * 0.2
          }}
        />
      ))}
    </div>
  );
};

// Progress bar with steps
export const StepProgress = ({ 
  currentStep, 
  totalSteps, 
  steps = [],
  variant = 'default'
}) => {
  const progress = (currentStep / totalSteps) * 100;

  return (
    <div className="space-y-4">
      <div className="progress">
        <div 
          className="progress-bar"
          style={{ width: `${progress}%` }}
        />
      </div>
      
      {steps.length > 0 && (
        <div className="flex justify-between">
          {steps.map((step, index) => {
            const isActive = index + 1 === currentStep;
            const isCompleted = index + 1 < currentStep;
            
            return (
              <div 
                key={index}
                className={`flex flex-col items-center space-y-2 ${
                  variant === 'compact' ? 'text-xs' : 'text-sm'
                }`}
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 transition-all ${
                  isCompleted ? 'bg-success-600 border-success-600 text-white' :
                  isActive ? 'bg-primary-600 border-primary-600 text-white' :
                  'bg-neutral-200 border-neutral-300 text-neutral-500'
                }`}>
                  {isCompleted ? (
                    <CheckCircleIcon className="h-4 w-4" />
                  ) : (
                    <span className="font-medium">{index + 1}</span>
                  )}
                </div>
                <span className={`font-medium text-center ${
                  isActive ? 'text-primary-700' :
                  isCompleted ? 'text-success-700' :
                  'text-neutral-500'
                }`}>
                  {step}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

// Lazy loading wrapper
export const LazyLoader = ({ children, fallback = <InlineLoading /> }) => {
  const [isVisible, setIsVisible] = React.useState(false);
  const ref = React.useRef();

  React.useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <div ref={ref}>
      {isVisible ? children : fallback}
    </div>
  );
};

// Enhanced Empty State Component
export const EmptyState = ({ 
  icon: Icon = DocumentTextIcon,
  title = 'No data available',
  description = 'There is no data to display at the moment.',
  action = null,
  variant = 'default'
}) => {
  return (
    <div className={`text-center py-12 ${
      variant === 'card' ? 'card card-body' : ''
    }`}>
      <div className="mb-6">
        <div className="w-16 h-16 mx-auto bg-neutral-100 rounded-full flex items-center justify-center">
          <Icon className="h-8 w-8 text-neutral-400" />
        </div>
      </div>
      <div className="space-y-3">
        <h3 className="heading-lg text-neutral-900">{title}</h3>
        <p className="body-base text-neutral-600 max-w-md mx-auto">{description}</p>
        {action && (
          <div className="pt-4">
            {action}
          </div>
        )}
      </div>
    </div>
  );
};

export default {
  LoadingSpinner,
  LoadingButton,
  PageLoadingSkeleton,
  CardLoadingSkeleton,
  TableLoadingSkeleton,
  FullPageLoading,
  InlineLoading,
  LoadingOverlay,
  AIProcessingLoader,
  ProgressiveImage,
  StepProgress,
  EmptyState
};