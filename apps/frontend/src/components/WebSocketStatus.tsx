import React from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { RetroBadge } from './atoms/RetroBadge';
import { RetroButton } from './atoms/RetroButton';
import { RetroCard } from './atoms/RetroCard';

export const WebSocketStatus: React.FC = () => {
  const {
    isConnected,
    isConnecting,
    connectionStatus,
    error,
    retryCount,
    maxRetries,
    retryConnection,
    resetError,
  } = useWebSocket();

  const getStatusColor = () => {
    if (isConnected) return 'success';
    if (isConnecting) return 'warning';
    if (error) return 'danger';
    return 'info';
  };

  const getStatusText = () => {
    if (isConnected) return 'Connected';
    if (isConnecting) return 'Connecting...';
    if (error) return 'Error';
    return 'Disconnected';
  };

  const getStatusIcon = () => {
    if (isConnected) return '🔗';
    if (isConnecting) return '⏳';
    if (error) return '❌';
    return '🔌';
  };

  return (
    <RetroCard className='p-4'>
      <div className='flex items-center justify-between mb-4'>
        <h3 className='text-lg font-bold text-gray-800'>WebSocket Status</h3>
        <RetroBadge
          variant={getStatusColor()}
          className='flex items-center gap-2'
        >
          <span>{getStatusIcon()}</span>
          {getStatusText()}
        </RetroBadge>
      </div>

      <div className='space-y-3'>
        {/* Connection Details */}
        <div className='flex justify-between text-sm'>
          <span className='text-gray-600'>Status:</span>
          <span className='font-mono'>{connectionStatus}</span>
        </div>

        {/* Retry Information */}
        {retryCount > 0 && (
          <div className='flex justify-between text-sm'>
            <span className='text-gray-600'>Retry Attempts:</span>
            <span className='font-mono'>
              {retryCount} / {maxRetries}
            </span>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className='bg-red-50 border border-red-200 rounded-md p-3'>
            <div className='flex items-start'>
              <div className='flex-shrink-0'>
                <span className='text-red-400'>⚠️</span>
              </div>
              <div className='ml-3'>
                <h4 className='text-sm font-medium text-red-800'>
                  Connection Error
                </h4>
                <p className='text-sm text-red-700 mt-1'>{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className='flex gap-2 pt-2'>
          {!isConnected && !isConnecting && (
            <RetroButton
              onClick={retryConnection}
              disabled={retryCount >= maxRetries}
              className='flex-1'
            >
              {retryCount >= maxRetries
                ? 'Max Retries Reached'
                : 'Retry Connection'}
            </RetroButton>
          )}

          {error && (
            <RetroButton
              onClick={resetError}
              variant='secondary'
              className='flex-1'
            >
              Reset Error
            </RetroButton>
          )}
        </div>

        {/* Connection Tips */}
        {!isConnected && (
          <div className='bg-blue-50 border border-blue-200 rounded-md p-3'>
            <div className='flex items-start'>
              <div className='flex-shrink-0'>
                <span className='text-blue-400'>💡</span>
              </div>
              <div className='ml-3'>
                <h4 className='text-sm font-medium text-blue-800'>
                  Connection Tips
                </h4>
                <ul className='text-sm text-blue-700 mt-1 space-y-1'>
                  <li>• Check your internet connection</li>
                  <li>• Verify the backend service is running</li>
                  <li>• Ensure your authentication token is valid</li>
                  <li>• Try refreshing the page if issues persist</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </RetroCard>
  );
};

export default WebSocketStatus;
