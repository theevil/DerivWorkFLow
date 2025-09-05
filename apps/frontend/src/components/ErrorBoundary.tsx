import React, { Component, ErrorInfo, ReactNode } from 'react';
import { RetroCard } from './atoms/RetroCard';
import { RetroButton } from './atoms/RetroButton';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  resetOnPropsChange?: boolean;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
      errorId: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to console
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    // Update state with error info
    this.setState({
      errorInfo,
    });

    // Call custom error handler if provided
    this.props.onError?.(error, errorInfo);

    // Log to external service (you can implement this)
    this.logErrorToService(error, errorInfo);
  }

  componentDidUpdate(prevProps: Props) {
    // Reset error state if props changed and resetOnPropsChange is true
    if (this.props.resetOnPropsChange && prevProps !== this.props) {
      this.setState({
        hasError: false,
        error: null,
        errorInfo: null,
        errorId: null,
      });
    }
  }

  private logErrorToService(error: Error, errorInfo: ErrorInfo) {
    // You can implement logging to external services here
    // For example: Sentry, LogRocket, etc.
    try {
      const errorData = {
        errorId: this.state.errorId,
        message: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
      };

      // Log to console for development
      if (false) {
        console.group('Error Details');
        console.log('Error ID:', errorData.errorId);
        console.log('Error:', errorData);
        console.groupEnd();
      }

      // You can send this to your backend or external service
      // fetch('/api/errors', { method: 'POST', body: JSON.stringify(errorData) });
    } catch (loggingError) {
      console.error('Failed to log error:', loggingError);
    }
  }

  private handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null,
    });
  };

  private handleReload = () => {
    window.location.reload();
  };

  private handleGoHome = () => {
    window.location.href = '/';
  };

  private handleReportError = () => {
    const errorData = {
      errorId: this.state.errorId,
      message: this.state.error?.message,
      stack: this.state.error?.stack,
      componentStack: this.state.errorInfo?.componentStack,
      url: window.location.href,
      timestamp: new Date().toISOString(),
    };

    // Create a mailto link with error details
    const subject = `Error Report - ${errorData.errorId}`;
    const body = `Error Details:\n\nError ID: ${errorData.errorId}\nMessage: ${errorData.message}\nURL: ${errorData.url}\nTimestamp: ${errorData.timestamp}\n\nStack Trace:\n${errorData.stack}\n\nComponent Stack:\n${errorData.componentStack}`;

    const mailtoLink = `mailto:support@yourdomain.com?subject=${encodeURIComponent(
      subject
    )}&body=${encodeURIComponent(body)}`;

    window.open(mailtoLink);
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <div className='min-h-screen bg-gray-50 flex items-center justify-center p-4'>
          <RetroCard className='max-w-2xl w-full p-8'>
            <div className='text-center'>
              {/* Error Icon */}
              <div className='mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-6'>
                <svg
                  className='h-8 w-8 text-red-600'
                  fill='none'
                  viewBox='0 0 24 24'
                  stroke='currentColor'
                >
                  <path
                    strokeLinecap='round'
                    strokeLinejoin='round'
                    strokeWidth={2}
                    d='M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z'
                  />
                </svg>
              </div>

              {/* Error Title */}
              <h1 className='text-2xl font-bold text-gray-900 mb-4'>
                Oops! Something went wrong
              </h1>

              {/* Error Message */}
              <p className='text-gray-600 mb-6'>
                We're sorry, but something unexpected happened. Our team has
                been notified and is working to fix this issue.
              </p>

              {/* Error ID */}
              {this.state.errorId && (
                <div className='bg-gray-100 rounded-lg p-3 mb-6'>
                  <p className='text-sm text-gray-600'>
                    <span className='font-medium'>Error ID:</span>{' '}
                    {this.state.errorId}
                  </p>
                  <p className='text-xs text-gray-500 mt-1'>
                    Please include this ID when reporting the issue
                  </p>
                </div>
              )}

              {/* Error Details (Development Only) */}
              {false && this.state.error && (
                <div className='error-details'>
                  <h3>Error Details:</h3>
                  <pre>
                    {String(this.state.error?.message || this.state.error)}
                  </pre>
                  {false && this.state.error && (
                    <details>
                      <summary>Stack Trace</summary>
                      <pre>{this.state.errorInfo?.componentStack}</pre>
                    </details>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className='flex flex-col sm:flex-row gap-3 justify-center'>
                <RetroButton
                  onClick={this.handleReset}
                  className='flex-1 sm:flex-none'
                >
                  Try Again
                </RetroButton>

                <RetroButton
                  onClick={this.handleGoHome}
                  variant='secondary'
                  className='flex-1 sm:flex-none'
                >
                  Go Home
                </RetroButton>

                <RetroButton
                  onClick={this.handleReload}
                  variant='secondary'
                  className='flex-1 sm:flex-none'
                >
                  Reload Page
                </RetroButton>
              </div>

              {/* Report Error */}
              <div className='mt-6 pt-6 border-t border-gray-200'>
                <p className='text-sm text-gray-500 mb-3'>
                  If this problem persists, please report it to our support team
                </p>
                <RetroButton
                  onClick={this.handleReportError}
                  variant='secondary'
                  size='sm'
                >
                  Report Error
                </RetroButton>
              </div>
            </div>
          </RetroCard>
        </div>
      );
    }

    return this.props.children;
  }
}

// Higher-order component for wrapping components with error boundary
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  fallback?: ReactNode,
  onError?: (error: Error, errorInfo: ErrorInfo) => void
) {
  const WrappedComponent = (props: P) => (
    <ErrorBoundary fallback={fallback} onError={onError}>
      <Component {...props} />
    </ErrorBoundary>
  );

  WrappedComponent.displayName = `withErrorBoundary(${
    Component.displayName || Component.name
  })`;

  return WrappedComponent;
}

// Hook for handling errors in functional components
export function useErrorHandler() {
  const [error, setError] = React.useState<Error | null>(null);

  const handleError = React.useCallback((error: Error) => {
    console.error('Error caught by useErrorHandler:', error);
    setError(error);
  }, []);

  const clearError = React.useCallback(() => {
    setError(null);
  }, []);

  return {
    error,
    handleError,
    clearError,
    hasError: !!error,
  };
}

export default ErrorBoundary;
