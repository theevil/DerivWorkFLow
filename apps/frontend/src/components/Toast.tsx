import React, { useEffect } from 'react';
import { useAppSelector, useAppDispatch } from '../hooks';
import { selectToasts, removeToast, hideToast } from '../store';
import { RetroCard } from './atoms/RetroCard';

// Toast component
export const Toast: React.FC = () => {
  const toasts = useAppSelector(selectToasts);
  const dispatch = useAppDispatch();

  // Auto-hide toasts after their duration
  useEffect(() => {
    toasts.forEach(toast => {
      if (toast.isVisible) {
        const timer = setTimeout(() => {
          dispatch(hideToast(toast.id));

          // Remove toast after hiding animation
          setTimeout(() => {
            dispatch(removeToast(toast.id));
          }, 300);
        }, toast.duration);

        return () => clearTimeout(timer);
      }
    });
  }, [toasts, dispatch]);

  // Get toast icon based on type
  const getToastIcon = (type: string) => {
    switch (type) {
      case 'success':
        return (
          <svg
            className='w-5 h-5 text-green-500'
            fill='currentColor'
            viewBox='0 0 20 20'
          >
            <path
              fillRule='evenodd'
              d='M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z'
              clipRule='evenodd'
            />
          </svg>
        );
      case 'error':
        return (
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
        );
      case 'warning':
        return (
          <svg
            className='h-8 w-8 text-yellow-600'
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
        );
      case 'info':
        return (
          <svg
            className='h-8 w-8 text-blue-600'
            fill='none'
            viewBox='0 0 24 24'
            stroke='currentColor'
          >
            <path
              strokeLinecap='round'
              strokeLinejoin='round'
              strokeWidth={2}
              d='M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
            />
          </svg>
        );
      default:
        return null;
    }
  };

  // Get toast background color based on type
  const getToastBackground = (type: string) => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200';
      case 'error':
        return 'bg-red-50 border-red-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      case 'info':
        return 'bg-blue-50 border-blue-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  // Get toast text color based on type
  const getToastTextColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'text-green-800';
      case 'error':
        return 'text-red-800';
      case 'warning':
        return 'text-yellow-800';
      case 'info':
        return 'text-blue-800';
      default:
        return 'text-gray-800';
    }
  };

  // Handle manual close
  const handleClose = (toastId: string) => {
    dispatch(hideToast(toastId));
    setTimeout(() => {
      dispatch(removeToast(toastId));
    }, 300);
  };

  if (toasts.length === 0) return null;

  return (
    <div className='fixed top-4 right-4 z-50 space-y-2 max-w-sm'>
      {toasts.map(toast => (
        <div
          key={toast.id}
          className={`transform transition-all duration-300 ease-in-out ${
            toast.isVisible
              ? 'translate-x-0 opacity-100'
              : 'translate-x-full opacity-0'
          }`}
        >
          <RetroCard
            className={`${getToastBackground(
              toast.type
            )} border-l-4 border-l-current`}
          >
            <div className='flex items-start space-x-3'>
              <div className='flex-shrink-0'>{getToastIcon(toast.type)}</div>

              <div className='flex-1 min-w-0'>
                <h4
                  className={`text-sm font-medium ${getToastTextColor(
                    toast.type
                  )}`}
                >
                  {toast.title}
                </h4>
                {toast.message && (
                  <p
                    className={`text-sm ${getToastTextColor(
                      toast.type
                    )} opacity-90 mt-1`}
                  >
                    {toast.message}
                  </p>
                )}
              </div>

              <button
                onClick={() => handleClose(toast.id)}
                className='flex-shrink-0 ml-2 text-gray-400 hover:text-gray-600 transition-colors'
                title='Close notification'
                aria-label='Close notification'
              >
                <svg
                  className='w-4 h-4'
                  fill='currentColor'
                  viewBox='0 0 20 20'
                >
                  <path
                    fillRule='evenodd'
                    d='M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z'
                    clipRule='evenodd'
                  />
                </svg>
              </button>
            </div>
          </RetroCard>
        </div>
      ))}
    </div>
  );
};

export default Toast;
