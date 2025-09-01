import { useEffect, useRef, useState, useCallback } from 'react';
import { useAuthStore } from '../stores/auth';
import { 
  getWebSocketClient, 
  disconnectWebSocket, 
  WebSocketClient, 
  WebSocketMessage,
  TickData,
  PortfolioData 
} from '../lib/websocket';

export interface UseWebSocketReturn {
  isConnected: boolean;
  isConnecting: boolean;
  client: WebSocketClient | null;
  connectionStatus: string;
  subscribeToTicks: (symbol: string) => void;
  unsubscribeFromTicks: (symbol: string) => void;
  buyContract: (contractData: any) => void;
  sellContract: (contractId: string, price?: number) => void;
  getPortfolio: () => void;
}

export const useWebSocket = () => {
  const { token, isAuthenticated } = useAuthStore();
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const clientRef = useRef<WebSocketClient | null>(null);

  // Event handlers
  const handleConnection = useCallback((message: WebSocketMessage) => {
    setIsConnected(true);
    setIsConnecting(false);
    setConnectionStatus('connected');
    console.log('WebSocket connected successfully');
  }, []);

  const handleDisconnection = useCallback((message: WebSocketMessage) => {
    setIsConnected(false);
    setIsConnecting(false);
    setConnectionStatus('disconnected');
    console.log('WebSocket disconnected');
  }, []);

  const handleError = useCallback((message: WebSocketMessage) => {
    setIsConnecting(false);
    setConnectionStatus('error');
    console.error('WebSocket error:', message.message);
  }, []);

  const handleTick = useCallback((message: WebSocketMessage) => {
    // Handle tick data
    if (message.data) {
      const tickData = message.data as TickData;
      console.log('Tick received:', tickData);
      // You can emit this to a global state or event system
      window.dispatchEvent(new CustomEvent('tick-data', { detail: tickData }));
    }
  }, []);

  const handlePortfolio = useCallback((message: WebSocketMessage) => {
    // Handle portfolio data
    if (message.data) {
      const portfolioData = message.data as PortfolioData;
      console.log('Portfolio update:', portfolioData);
      // Emit to global state
      window.dispatchEvent(new CustomEvent('portfolio-update', { detail: portfolioData }));
    }
  }, []);

  const handleBuyResponse = useCallback((message: WebSocketMessage) => {
    console.log('Buy response:', message.data);
    window.dispatchEvent(new CustomEvent('buy-response', { detail: message.data }));
  }, []);

  const handleSellResponse = useCallback((message: WebSocketMessage) => {
    console.log('Sell response:', message.data);
    window.dispatchEvent(new CustomEvent('sell-response', { detail: message.data }));
  }, []);

  // Initialize WebSocket connection
  useEffect(() => {
    if (isAuthenticated && token && !clientRef.current) {
      setIsConnecting(true);
      setConnectionStatus('connecting');
      
      const client = getWebSocketClient(token);
      clientRef.current = client;

      // Set up event handlers
      client.on('connection', handleConnection);
      client.on('disconnection', handleDisconnection);
      client.on('error', handleError);
      client.on('tick', handleTick);
      client.on('portfolio', handlePortfolio);
      client.on('buy_response', handleBuyResponse);
      client.on('sell_response', handleSellResponse);

      // Connect
      client.connect()
        .then((success) => {
          if (success) {
            console.log('WebSocket connection established');
          } else {
            setIsConnecting(false);
            setConnectionStatus('failed');
          }
        })
        .catch((error) => {
          console.error('Failed to connect WebSocket:', error);
          setIsConnecting(false);
          setConnectionStatus('failed');
        });
    }

    return () => {
      // Cleanup event handlers when component unmounts or token changes
      if (clientRef.current) {
        clientRef.current.off('connection', handleConnection);
        clientRef.current.off('disconnection', handleDisconnection);
        clientRef.current.off('error', handleError);
        clientRef.current.off('tick', handleTick);
        clientRef.current.off('portfolio', handlePortfolio);
        clientRef.current.off('buy_response', handleBuyResponse);
        clientRef.current.off('sell_response', handleSellResponse);
      }
    };
  }, [isAuthenticated, token, handleConnection, handleDisconnection, handleError, handleTick, handlePortfolio, handleBuyResponse, handleSellResponse]);

  // Disconnect when user logs out
  useEffect(() => {
    if (!isAuthenticated) {
      if (clientRef.current) {
        disconnectWebSocket();
        clientRef.current = null;
      }
      setIsConnected(false);
      setIsConnecting(false);
      setConnectionStatus('disconnected');
    }
  }, [isAuthenticated]);

  // Trading methods
  const subscribeToTicks = useCallback((symbol: string) => {
    if (clientRef.current && isConnected) {
      clientRef.current.subscribeToTicks(symbol);
    }
  }, [isConnected]);

  const unsubscribeFromTicks = useCallback((symbol: string) => {
    if (clientRef.current && isConnected) {
      clientRef.current.unsubscribeFromTicks(symbol);
    }
  }, [isConnected]);

  const buyContract = useCallback((contractData: any) => {
    if (clientRef.current && isConnected) {
      clientRef.current.buyContract(contractData);
    }
  }, [isConnected]);

  const sellContract = useCallback((contractId: string, price?: number) => {
    if (clientRef.current && isConnected) {
      clientRef.current.sellContract(contractId, price);
    }
  }, [isConnected]);

  const getPortfolio = useCallback(() => {
    if (clientRef.current && isConnected) {
      clientRef.current.getPortfolio();
    }
  }, [isConnected]);

  return {
    isConnected,
    isConnecting,
    client: clientRef.current,
    connectionStatus,
    subscribeToTicks,
    unsubscribeFromTicks,
    buyContract,
    sellContract,
    getPortfolio,
  };
};

// Custom hook for listening to specific WebSocket events
export const useWebSocketEvent = (eventType: string, handler: (data: any) => void) => {
  useEffect(() => {
    const handleEvent = (event: CustomEvent) => {
      handler(event.detail);
    };

    window.addEventListener(eventType, handleEvent as EventListener);
    
    return () => {
      window.removeEventListener(eventType, handleEvent as EventListener);
    };
  }, [eventType, handler]);
};

