import React from 'react';
import { AlertTriangle, RefreshCw, Home, Bug } from 'lucide-react';
import { motion } from 'framer-motion';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      eventId: null
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error,
      errorInfo
    });

    // Log error to monitoring service (e.g., Sentry)
    if (typeof window !== 'undefined' && window.Sentry) {
      const eventId = window.Sentry.captureException(error, {
        contexts: {
          react: {
            componentStack: errorInfo.componentStack
          }
        }
      });
      this.setState({ eventId });
    }

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Error Boundary caught an error:', error, errorInfo);
    }
  }

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  handleReportBug = () => {
    if (this.state.eventId && window.Sentry) {
      window.Sentry.showReportDialog({ eventId: this.state.eventId });
    } else {
      // Fallback: open email client
      const subject = encodeURIComponent('Bug Report: Application Error');
      const body = encodeURIComponent(`
Error Details:
${this.state.error?.message || 'Unknown error'}

Stack Trace:
${this.state.error?.stack || 'Not available'}

Component Stack:
${this.state.errorInfo?.componentStack || 'Not available'}

Please describe what you were doing when this error occurred:
      `);
      window.location.href = `mailto:support@yourdomain.com?subject=${subject}&body=${body}`;
    }
  };

  render() {
    if (this.state.hasError) {
      const { fallback: Fallback, showDetails = false } = this.props;

      // Use custom fallback if provided
      if (Fallback) {
        return (
          <Fallback 
            error={this.state.error} 
            errorInfo={this.state.errorInfo}
            onReload={this.handleReload}
            onGoHome={this.handleGoHome}
            onReportBug={this.handleReportBug}
          />
        );
      }

      // Default error UI
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-md w-full bg-white rounded-lg shadow-lg p-6 text-center"
          >
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                <AlertTriangle className="w-8 h-8 text-red-600" />
              </div>
            </div>

            <h1 className="text-xl font-semibold text-gray-900 mb-2">
              Something went wrong
            </h1>

            <p className="text-gray-600 mb-6">
              We're sorry, but something unexpected happened. Please try refreshing the page.
            </p>

            <div className="space-y-3">
              <button
                onClick={this.handleReload}
                className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh Page
              </button>

              <button
                onClick={this.handleGoHome}
                className="w-full flex items-center justify-center px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
              >
                <Home className="w-4 h-4 mr-2" />
                Go to Homepage
              </button>

              <button
                onClick={this.handleReportBug}
                className="w-full flex items-center justify-center px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 transition-colors"
              >
                <Bug className="w-4 h-4 mr-2" />
                Report This Issue
              </button>
            </div>

            {/* Error Details (Development/Debug Mode) */}
            {(showDetails || process.env.NODE_ENV === 'development') && this.state.error && (
              <details className="mt-6 text-left">
                <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
                  Error Details (for developers)
                </summary>
                <div className="mt-2 p-3 bg-gray-100 rounded-md text-xs font-mono text-gray-800 overflow-auto max-h-40">
                  <div className="mb-2">
                    <strong>Error:</strong> {this.state.error.message}
                  </div>
                  <div className="mb-2">
                    <strong>Stack:</strong>
                    <pre className="whitespace-pre-wrap mt-1">
                      {this.state.error.stack}
                    </pre>
                  </div>
                  {this.state.errorInfo && (
                    <div>
                      <strong>Component Stack:</strong>
                      <pre className="whitespace-pre-wrap mt-1">
                        {this.state.errorInfo.componentStack}
                      </pre>
                    </div>
                  )}
                </div>
              </details>
            )}

            {this.state.eventId && (
              <p className="mt-4 text-xs text-gray-500">
                Error ID: {this.state.eventId}
              </p>
            )}
          </motion.div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Hook for functional components
export const useErrorHandler = () => {
  const handleError = React.useCallback((error, errorInfo) => {
    if (typeof window !== 'undefined' && window.Sentry) {
      window.Sentry.captureException(error, {
        contexts: {
          react: {
            componentStack: errorInfo?.componentStack
          }
        }
      });
    }

    console.error('Error caught by error handler:', error, errorInfo);
  }, []);

  return handleError;
};

// Higher-order component for wrapping components with error boundary
export const withErrorBoundary = (Component, errorBoundaryProps = {}) => {
  const WrappedComponent = (props) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </ErrorBoundary>
  );

  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;
  
  return WrappedComponent;
};

// Specific error boundary for async operations
export class AsyncErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Async Error Boundary caught an error:', error, errorInfo);
    
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback(this.state.error);
      }

      return (
        <div className="p-4 bg-red-50 border border-red-200 rounded-md">
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-red-600 mr-2" />
            <p className="text-red-800 font-medium">Failed to load content</p>
          </div>
          <p className="text-red-600 text-sm mt-1">
            {this.state.error?.message || 'An unexpected error occurred'}
          </p>
          {this.props.onRetry && (
            <button
              onClick={() => {
                this.setState({ hasError: false, error: null });
                this.props.onRetry();
              }}
              className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
            >
              Try again
            </button>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;