/**
 * Hook for WebSocket connection to receive real-time automation updates
 */

import { useEffect, useRef, useState } from 'react';
import { useAutomationStore } from '../stores/automation';
import { config } from '../config/env';
import type { AutomationWebSocketMessage, AutomationUpdate } from '../types/automation';

interface UseAutomationWebSocketOptions {
  enabled?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export function useAutomationWebSocket(options: UseAutomationWebSocketOptions = {}) {
  const {
    enabled = true,
    reconnectInterval = 5000,
    maxReconnectAttempts = 10
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const { setConnected, updateLastUpdate, loadAlerts, refreshSystemStatus } = useAutomationStore();

  const connect = () => {
    if (!enabled || wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      // Construct WebSocket URL (assuming same host as API)
      const wsUrl = config.apiUrl.replace('http', 'ws') + '/automation';
      
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('Automation WebSocket connected');
        setIsConnected(true);
        setError(null);
        setReconnectAttempts(0);
        setConnected(true);
        updateLastUpdate();
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message: AutomationWebSocketMessage = JSON.parse(event.data);
          handleMessage(message);
          updateLastUpdate();
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      wsRef.current.onclose = (event) => {
        console.log('Automation WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);
        setConnected(false);

        // Attempt to reconnect if enabled and within retry limits
        if (enabled && reconnectAttempts < maxReconnectAttempts) {
          setReconnectAttempts(prev => prev + 1);
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        } else if (reconnectAttempts >= maxReconnectAttempts) {
          setError('Max reconnection attempts reached');
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('Automation WebSocket error:', error);
        setError('WebSocket connection error');
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setError('Failed to create WebSocket connection');
    }
  };

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect');
      wsRef.current = null;
    }

    setIsConnected(false);
    setConnected(false);
  };

  const handleMessage = (message: AutomationWebSocketMessage) => {
    const { type, data } = message;

    if (type === 'automation_update') {
      handleAutomationUpdate(data);
    }
  };

  const handleAutomationUpdate = (update: AutomationUpdate) => {
    const { type, data } = update;

    switch (type) {
      case 'signal_generated':
        // New signal generated
        console.log('New trading signal generated:', data);
        // Could trigger a notification here
        break;

      case 'trade_executed':
        // Trade executed successfully
        console.log('Trade executed:', data);
        // Refresh system status to show updated execution count
        refreshSystemStatus();
        break;

      case 'position_closed':
        // Position closed
        console.log('Position closed:', data);
        // Refresh system status
        refreshSystemStatus();
        break;

      case 'alert_created':
        // New alert created
        console.log('New alert created:', data);
        // Reload alerts to show the new one
        loadAlerts();
        break;

      default:
        console.log('Unknown automation update type:', type);
    }
  };

  // Send message through WebSocket
  const sendMessage = (message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  };

  // Subscribe to specific automation events
  const subscribe = (eventTypes: string[]) => {
    sendMessage({
      type: 'subscribe',
      events: eventTypes
    });
  };

  // Unsubscribe from specific automation events
  const unsubscribe = (eventTypes: string[]) => {
    sendMessage({
      type: 'unsubscribe',
      events: eventTypes
    });
  };

  // Connect on mount if enabled
  useEffect(() => {
    if (enabled) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [enabled]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, []);

  return {
    isConnected,
    error,
    reconnectAttempts,
    connect,
    disconnect,
    sendMessage,
    subscribe,
    unsubscribe,
  };
}

// Hook for automation notifications
export function useAutomationNotifications() {
  const { isConnected } = useAutomationWebSocket();
  const [notifications, setNotifications] = useState<AutomationUpdate[]>([]);

  const addNotification = (update: AutomationUpdate) => {
    setNotifications(prev => [update, ...prev.slice(0, 49)]); // Keep last 50
  };

  const clearNotifications = () => {
    setNotifications([]);
  };

  const removeNotification = (index: number) => {
    setNotifications(prev => prev.filter((_, i) => i !== index));
  };

  return {
    isConnected,
    notifications,
    addNotification,
    clearNotifications,
    removeNotification,
  };
}
