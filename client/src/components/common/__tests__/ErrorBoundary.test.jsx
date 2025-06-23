import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import ErrorBoundary, { useErrorHandler, withErrorBoundary, AsyncErrorBoundary } from '../ErrorBoundary';

// Mock console.error to avoid noise in tests
const originalConsoleError = console.error;
beforeAll(() => {
  console.error = vi.fn();
});

afterAll(() => {
  console.error = originalConsoleError;
});

// Component that throws an error
const ThrowError = ({ shouldThrow = false }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
};

// Component that uses error handler hook
const ComponentWithErrorHandler = () => {
  const handleError = useErrorHandler();
  
  return (
    <button onClick={() => handleError(new Error('Hook error'))}>
      Trigger Error
    </button>
  );
};

describe('ErrorBoundary', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <div>Test content</div>
      </ErrorBoundary>
    );
    
    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  it('renders error UI when child component throws', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText('Refresh Page')).toBeInTheDocument();
    expect(screen.getByText('Go to Homepage')).toBeInTheDocument();
    expect(screen.getByText('Report This Issue')).toBeInTheDocument();
  });

  it('calls onReload when refresh button is clicked', async () => {
    const user = userEvent.setup();
    
    // Mock window.location.reload
    Object.defineProperty(window, 'location', {
      value: { reload: vi.fn() },
      writable: true,
    });
    
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    
    const refreshButton = screen.getByText('Refresh Page');
    await user.click(refreshButton);
    
    expect(window.location.reload).toHaveBeenCalled();
  });

  it('redirects to home when go home button is clicked', async () => {
    const user = userEvent.setup();
    
    // Mock window.location.href
    Object.defineProperty(window, 'location', {
      value: { href: '' },
      writable: true,
    });
    
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    
    const homeButton = screen.getByText('Go to Homepage');
    await user.click(homeButton);
    
    expect(window.location.href).toBe('/');
  });

  it('uses custom fallback when provided', () => {
    const CustomFallback = ({ error }) => (
      <div>Custom error: {error?.message}</div>
    );
    
    render(
      <ErrorBoundary fallback={CustomFallback}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('Custom error: Test error')).toBeInTheDocument();
  });

  it('shows error details in development mode', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';
    
    render(
      <ErrorBoundary showDetails={true}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('Error Details (for developers)')).toBeInTheDocument();
    
    process.env.NODE_ENV = originalEnv;
  });

  it('logs error to console', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    
    expect(console.error).toHaveBeenCalled();
  });
});

describe('useErrorHandler', () => {
  it('handles errors without crashing', async () => {
    const user = userEvent.setup();
    
    render(<ComponentWithErrorHandler />);
    
    const button = screen.getByText('Trigger Error');
    await user.click(button);
    
    expect(console.error).toHaveBeenCalled();
  });
});

describe('withErrorBoundary', () => {
  it('wraps component with error boundary', () => {
    const WrappedComponent = withErrorBoundary(ThrowError);
    
    render(<WrappedComponent shouldThrow={false} />);
    
    expect(screen.getByText('No error')).toBeInTheDocument();
  });

  it('catches errors in wrapped component', () => {
    const WrappedComponent = withErrorBoundary(ThrowError);
    
    render(<WrappedComponent shouldThrow={true} />);
    
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });
});

describe('AsyncErrorBoundary', () => {
  it('renders children when there is no error', () => {
    render(
      <AsyncErrorBoundary>
        <div>Async content</div>
      </AsyncErrorBoundary>
    );
    
    expect(screen.getByText('Async content')).toBeInTheDocument();
  });

  it('renders error UI when child component throws', () => {
    render(
      <AsyncErrorBoundary>
        <ThrowError shouldThrow={true} />
      </AsyncErrorBoundary>
    );
    
    expect(screen.getByText('Failed to load content')).toBeInTheDocument();
  });

  it('uses custom fallback when provided', () => {
    const customFallback = (error) => <div>Async error: {error?.message}</div>;
    
    render(
      <AsyncErrorBoundary fallback={customFallback}>
        <ThrowError shouldThrow={true} />
      </AsyncErrorBoundary>
    );
    
    expect(screen.getByText('Async error: Test error')).toBeInTheDocument();
  });

  it('calls onError callback when error occurs', () => {
    const onError = vi.fn();
    
    render(
      <AsyncErrorBoundary onError={onError}>
        <ThrowError shouldThrow={true} />
      </AsyncErrorBoundary>
    );
    
    expect(onError).toHaveBeenCalled();
  });

  it('shows retry button when onRetry is provided', async () => {
    const user = userEvent.setup();
    const onRetry = vi.fn();
    
    render(
      <AsyncErrorBoundary onRetry={onRetry}>
        <ThrowError shouldThrow={true} />
      </AsyncErrorBoundary>
    );
    
    const retryButton = screen.getByText('Try again');
    await user.click(retryButton);
    
    expect(onRetry).toHaveBeenCalled();
  });

  it('resets error state when retry is clicked', async () => {
    const user = userEvent.setup();
    let shouldThrow = true;
    const onRetry = vi.fn(() => {
      shouldThrow = false;
    });
    
    const { rerender } = render(
      <AsyncErrorBoundary onRetry={onRetry}>
        <ThrowError shouldThrow={shouldThrow} />
      </AsyncErrorBoundary>
    );
    
    expect(screen.getByText('Failed to load content')).toBeInTheDocument();
    
    const retryButton = screen.getByText('Try again');
    await user.click(retryButton);
    
    // Rerender with shouldThrow = false
    rerender(
      <AsyncErrorBoundary onRetry={onRetry}>
        <ThrowError shouldThrow={false} />
      </AsyncErrorBoundary>
    );
    
    expect(screen.getByText('No error')).toBeInTheDocument();
  });
});