import { useState, useEffect, useCallback } from 'react';
import { Button, Select, NumberInput, Badge } from '@mantine/core';
import { IconTrendingUp, IconTrendingDown, IconRefresh, IconActivity } from '@tabler/icons-react';
import { Layout } from '../components/Layout';
import { useWebSocket, useWebSocketEvent } from '../hooks/useWebSocket';
import { useAutomationStore, automationSelectors } from '../stores/automation';
import { EmergencyStopButton } from '../components/automation/EmergencyStopButton';
import { useAuthStore } from '../stores/auth';

interface MarketData {
  symbol: string;
  tick: number;
  ask: number;
  bid: number;
  quote: number;
  timestamp: number;
  change: number;
  changePercent: number;
}

interface ContractType {
  value: string;
  label: string;
  description: string;
}

const contractTypes: ContractType[] = [
  { value: 'CALL', label: 'Higher', description: 'Predict that the market will end higher' },
  { value: 'PUT', label: 'Lower', description: 'Predict that the market will end lower' }
];

const symbols = [
  'R_10', 'R_25', 'R_50', 'R_75', 'R_100',
  'BOOM_1000', 'CRASH_1000', 'STEP_10', 'STEP_25'
];

export function TradingPage() {
  const user = useAuthStore((state) => state.user);
  const [selectedSymbol, setSelectedSymbol] = useState('R_10');
  const [selectedContract, setSelectedContract] = useState('CALL');
  const [amount, setAmount] = useState(10);
  const [duration, setDuration] = useState(5);
  const [marketData, setMarketData] = useState<Map<string, MarketData>>(new Map());
  const [loading, setLoading] = useState(false);
  const [subscribedSymbols, setSubscribedSymbols] = useState<Set<string>>(new Set());

  // Automation state
  const { config: automationConfig } = useAutomationStore();
  const isAutoTradingEnabled = automationSelectors.isAutoTradingEnabled({ config: automationConfig } as any);

  // WebSocket connection
  const {
    isConnected,
    isConnecting,
    subscribeToTicks,
    unsubscribeFromTicks,
    buyContract
  } = useWebSocket();

  // Handle tick data from WebSocket
  useWebSocketEvent('tick-data', useCallback((tickData: any) => {
    const currentData = marketData.get(tickData.symbol) || {
      symbol: tickData.symbol,
      tick: 0,
      ask: 0,
      bid: 0,
      quote: 0,
      timestamp: 0,
      change: 0,
      changePercent: 0
    };

    const newTick = tickData.tick || tickData.quote;
    const change = newTick - currentData.tick;
    const changePercent = currentData.tick > 0 ? (change / currentData.tick) * 100 : 0;

    const newData: MarketData = {
      symbol: tickData.symbol,
      tick: newTick,
      ask: tickData.ask || newTick,
      bid: tickData.bid || newTick,
      quote: tickData.quote || newTick,
      timestamp: tickData.epoch || Date.now(),
      change: change,
      changePercent: changePercent
    };

    setMarketData(prev => new Map(prev.set(tickData.symbol, newData)));
  }, [marketData]));

  // Handle buy response
  useWebSocketEvent('buy-response', useCallback((response: any) => {
    console.log('Buy response:', response);
    setLoading(false);
    
    if (response.data && response.data.buy) {
      // Handle successful buy
      alert(`Contract purchased successfully! Contract ID: ${response.data.buy.contract_id}`);
    } else if (response.data && response.data.error) {
      // Handle error
      alert(`Error: ${response.data.error.message}`);
    }
  }, []));

  // Subscribe to selected symbol when it changes
  useEffect(() => {
    if (isConnected && selectedSymbol && !subscribedSymbols.has(selectedSymbol)) {
      subscribeToTicks(selectedSymbol);
      setSubscribedSymbols(prev => new Set(prev.add(selectedSymbol)));
    }
  }, [isConnected, selectedSymbol, subscribeToTicks, subscribedSymbols]);

  // Subscribe to all available symbols for market overview
  useEffect(() => {
    if (isConnected) {
      symbols.forEach(symbol => {
        if (!subscribedSymbols.has(symbol)) {
          subscribeToTicks(symbol);
          setSubscribedSymbols(prev => new Set(prev.add(symbol)));
        }
      });
    }
  }, [isConnected, subscribeToTicks, subscribedSymbols]);

  const handleBuyContract = async () => {
    if (!isConnected) {
      alert('WebSocket not connected. Please check your connection.');
      return;
    }

    setLoading(true);
    
    const success = buyContract({
      contract_type: selectedContract,
      symbol: selectedSymbol,
      amount: amount,
      duration: duration,
      duration_unit: 'S'
    });

    if (!success) {
      setLoading(false);
      alert('Failed to send buy request. Please try again.');
    }
  };

  const getCurrentMarketData = (symbol: string): MarketData | null => {
    return marketData.get(symbol) || null;
  };

  const formatPrice = (price: number) => {
    return price.toFixed(5);
  };

  const formatChange = (change: number, changePercent: number) => {
    const sign = change >= 0 ? '+' : '';
    return `${sign}${change.toFixed(5)} (${sign}${changePercent.toFixed(2)}%)`;
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Live Trading
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Trade with real-time market data
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-success-500' : isConnecting ? 'bg-warning-500' : 'bg-danger-500'
              }`}></div>
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {isConnected ? 'Live Data' : isConnecting ? 'Connecting...' : 'Offline'}
              </span>
            </div>
            
            <Badge 
              color={isConnected ? 'green' : 'red'} 
              variant="light"
              leftSection={<IconActivity size={12} />}
            >
              {subscribedSymbols.size} Symbols
            </Badge>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Trading Panel */}
          <div className="lg:col-span-1">
            <div className="card bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
                New Position
              </h3>
              
              <div className="space-y-4">
                {/* Symbol Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Symbol
                  </label>
                  <Select
                    value={selectedSymbol}
                    onChange={(value) => setSelectedSymbol(value || 'R_10')}
                    data={symbols.map(symbol => ({ value: symbol, label: symbol }))}
                    placeholder="Select symbol"
                  />
                </div>

                {/* Current Price Display */}
                {getCurrentMarketData(selectedSymbol) && (
                  <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Current Price</span>
                      <div className="text-right">
                        <div className="text-lg font-bold text-gray-900 dark:text-white">
                          {formatPrice(getCurrentMarketData(selectedSymbol)!.tick)}
                        </div>
                        <div className={`text-sm ${
                          getCurrentMarketData(selectedSymbol)!.change >= 0 
                            ? 'text-success-600' 
                            : 'text-danger-600'
                        }`}>
                          {formatChange(
                            getCurrentMarketData(selectedSymbol)!.change,
                            getCurrentMarketData(selectedSymbol)!.changePercent
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Contract Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Prediction
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {contractTypes.map((type) => (
                      <button
                        key={type.value}
                        onClick={() => setSelectedContract(type.value)}
                        className={`p-3 rounded-lg border-2 transition-colors ${
                          selectedContract === type.value
                            ? type.value === 'CALL'
                              ? 'border-success-500 bg-success-50 dark:bg-success-900/20'
                              : 'border-danger-500 bg-danger-50 dark:bg-danger-900/20'
                            : 'border-gray-200 dark:border-gray-600 hover:border-gray-300'
                        }`}
                      >
                        <div className="flex items-center justify-center space-x-2">
                          {type.value === 'CALL' ? (
                            <IconTrendingUp size={16} className="text-success-600" />
                          ) : (
                            <IconTrendingDown size={16} className="text-danger-600" />
                          )}
                          <span className="font-medium text-gray-900 dark:text-white">
                            {type.label}
                          </span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Amount */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Stake Amount ($)
                  </label>
                  <NumberInput
                    value={amount}
                    onChange={(value) => setAmount(Number(value) || 10)}
                    min={1}
                    max={1000}
                    step={1}
                    placeholder="Enter amount"
                  />
                </div>

                {/* Duration */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Duration (seconds)
                  </label>
                  <NumberInput
                    value={duration}
                    onChange={(value) => setDuration(Number(value) || 5)}
                    min={5}
                    max={300}
                    step={5}
                    placeholder="Enter duration"
                  />
                </div>

                {/* Buy Button */}
                <Button
                  fullWidth
                  onClick={handleBuyContract}
                  loading={loading}
                  disabled={!isConnected || loading}
                  className={selectedContract === 'CALL' ? 'btn-primary bg-success-600 hover:bg-success-700' : 'btn-primary bg-danger-600 hover:bg-danger-700'}
                  size="lg"
                >
                  {loading ? 'Processing...' : `Buy ${selectedContract} for $${amount}`}
                </Button>

                {/* Emergency Stop Button - Only show if auto trading is enabled */}
                {isAutoTradingEnabled && (
                  <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                    <EmergencyStopButton 
                      size="sm" 
                      variant="light" 
                      fullWidth
                    />
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Market Data */}
          <div className="lg:col-span-2">
            <div className="card bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Market Overview
                </h3>
                <Button
                  variant="light"
                  size="sm"
                  leftSection={<IconRefresh size={14} />}
                >
                  Refresh
                </Button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {symbols.map((symbol) => {
                  const data = getCurrentMarketData(symbol);
                  return (
                    <div
                      key={symbol}
                      className={`p-4 rounded-lg border-2 transition-colors cursor-pointer ${
                        selectedSymbol === symbol
                          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                          : 'border-gray-200 dark:border-gray-600 hover:border-gray-300'
                      }`}
                      onClick={() => setSelectedSymbol(symbol)}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-medium text-gray-900 dark:text-white">
                          {symbol}
                        </span>
                        {data && (
                          <div className={`w-2 h-2 rounded-full ${
                            Date.now() - data.timestamp < 10000 ? 'bg-success-500' : 'bg-gray-400'
                          }`} />
                        )}
                      </div>
                      
                      {data ? (
                        <>
                          <div className="text-xl font-bold text-gray-900 dark:text-white">
                            {formatPrice(data.tick)}
                          </div>
                          <div className={`text-sm ${
                            data.change >= 0 ? 'text-success-600' : 'text-danger-600'
                          }`}>
                            {formatChange(data.change, data.changePercent)}
                          </div>
                          <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            {new Date(data.timestamp).toLocaleTimeString()}
                          </div>
                        </>
                      ) : (
                        <div className="text-gray-500 dark:text-gray-400">
                          <div className="animate-pulse">
                            <div className="h-6 bg-gray-300 dark:bg-gray-600 rounded mb-2"></div>
                            <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded"></div>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Trading Tips */}
        <div className="card bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Trading Tips
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
              <h4 className="font-medium text-primary-900 dark:text-primary-100 mb-2">
                Risk Management
              </h4>
              <p className="text-sm text-primary-700 dark:text-primary-300">
                Never risk more than you can afford to lose. Start with small amounts.
              </p>
            </div>
            <div className="p-4 bg-warning-50 dark:bg-warning-900/20 rounded-lg">
              <h4 className="font-medium text-warning-900 dark:text-warning-100 mb-2">
                Market Analysis
              </h4>
              <p className="text-sm text-warning-700 dark:text-warning-300">
                Watch price movements and trends before making predictions.
              </p>
            </div>
            <div className="p-4 bg-success-50 dark:bg-success-900/20 rounded-lg">
              <h4 className="font-medium text-success-900 dark:text-success-100 mb-2">
                Live Data
              </h4>
              <p className="text-sm text-success-700 dark:text-success-300">
                Real-time prices update automatically via WebSocket connection.
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}

