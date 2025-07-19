"use client"

import React from 'react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertTriangle, RefreshCw, Wifi, WifiOff } from 'lucide-react';

interface AuthErrorBoundaryProps {
  children: React.ReactNode;
}

interface AuthErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
  isRetrying: boolean;
}

export class AuthErrorBoundary extends React.Component<
  AuthErrorBoundaryProps,
  AuthErrorBoundaryState
> {
  constructor(props: AuthErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      isRetrying: false,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<AuthErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('🚨 AuthErrorBoundary: Caught authentication error:', {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
    });

    this.setState({
      error,
      errorInfo,
    });
  }

  handleRetry = async () => {
    this.setState({ isRetrying: true });

    try {
      // Test connectivity
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000'}/health/simple`);
      
      if (response.ok) {
        // Reset error state and reload
        this.setState({
          hasError: false,
          error: null,
          errorInfo: null,
          isRetrying: false,
        });
      } else {
        throw new Error('Server is not responding');
      }
    } catch (error) {
      console.error('🔄 Retry failed:', error);
      setTimeout(() => {
        this.setState({ isRetrying: false });
      }, 2000);
    }
  };

  handleReload = () => {
    window.location.reload();
  };

  getErrorType = (): 'network' | 'auth' | 'unknown' => {
    const error = this.state.error;
    if (!error) return 'unknown';

    if (error.message.includes('fetch') || error.message.includes('Network')) {
      return 'network';
    }
    if (error.message.includes('Authentication') || error.message.includes('401')) {
      return 'auth';
    }
    return 'unknown';
  };

  render() {
    if (!this.state.hasError) {
      return this.props.children;
    }

    const errorType = this.getErrorType();
    const error = this.state.error;

    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-background">
        <div className="max-w-md w-full space-y-6">
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle className="flex items-center gap-2">
              {errorType === 'network' && <WifiOff className="h-4 w-4" />}
              {errorType === 'auth' && <AlertTriangle className="h-4 w-4" />}
              {errorType === 'network' ? 'Connection Error' : 
               errorType === 'auth' ? 'Authentication Error' : 'Application Error'}
            </AlertTitle>
            <AlertDescription className="mt-2">
              {errorType === 'network' && (
                <>
                  Unable to connect to the server. Please check your internet connection 
                  and verify that the backend server is running.
                </>
              )}
              {errorType === 'auth' && (
                <>
                  Authentication failed. Your session may have expired or there's an 
                  issue with the authentication service.
                </>
              )}
              {errorType === 'unknown' && (
                <>
                  An unexpected error occurred: {error?.message}
                </>
              )}
            </AlertDescription>
          </Alert>

          <div className="space-y-3">
            <Button 
              onClick={this.handleRetry} 
              disabled={this.state.isRetrying}
              className="w-full"
              variant="default"
            >
              {this.state.isRetrying ? (
                <>
                  <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                  Testing Connection...
                </>
              ) : (
                <>
                  <Wifi className="mr-2 h-4 w-4" />
                  Retry Connection
                </>
              )}
            </Button>

            <Button 
              onClick={this.handleReload} 
              variant="outline"
              className="w-full"
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Reload Application
            </Button>
          </div>

          {process.env.NODE_ENV === 'development' && (
            <details className="mt-4 p-4 bg-muted rounded-lg">
              <summary className="cursor-pointer text-sm font-medium">
                Error Details (Development)
              </summary>
              <div className="mt-2 text-xs">
                <p><strong>Error:</strong> {error?.message}</p>
                <p><strong>Stack:</strong></p>
                <pre className="whitespace-pre-wrap break-all">
                  {error?.stack}
                </pre>
                {this.state.errorInfo && (
                  <>
                    <p><strong>Component Stack:</strong></p>
                    <pre className="whitespace-pre-wrap break-all">
                      {this.state.errorInfo.componentStack}
                    </pre>
                  </>
                )}
              </div>
            </details>
          )}

          <div className="text-center text-sm text-muted-foreground">
            <p>If the problem persists, please contact support.</p>
            <p className="mt-1">
              Backend URL: {process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000'}
            </p>
          </div>
        </div>
      </div>
    );
  }
}