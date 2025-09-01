import { useState, useEffect } from 'react';
import { Button } from '@mantine/core';
import { IconRefresh, IconPlus, IconTrendingUp, IconBell, IconMoon, IconUser } from '@tabler/icons-react';
import type { TradePosition, TradingStats } from '../types/trading';
import { useAuthStore } from '../stores/auth';
import { api } from '../lib/api';
import { Layout } from '../components/Layout';
import { StatsGrid } from '../components/StatsGrid';
import { TradingCard } from '../components/TradingCard';
import { PerformanceChart } from '../components/PerformanceChart';

export function DashboardPage() {
  const user = useAuthStore((state) => state.user);
  const [positions, setPositions] = useState<TradePosition[]>([]);
  const [stats, setStats] = useState<TradingStats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      setLoading(true);
      // Mock data for now since we don't have real trading data yet
      const mockStats: TradingStats = {
        total_profit: 1250.50,
        total_trades: 45,
        win_rate: 0.67,
        avg_profit: 27.79,
        max_profit: 150.00,
        max_loss: -75.00,
        active_positions: 3,
      };

      const mockPositions: TradePosition[] = [
        {
          id: '1',
          user_id: user?.id || '',
          symbol: 'R_10',
          contract_type: 'CALL',
          amount: 50,
          entry_spot: 1.05423,
          current_spot: 1.05567,
          profit_loss: 12.50,
          status: 'open',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: '2',
          user_id: user?.id || '',
          symbol: 'BOOM_1000',
          contract_type: 'PUT',
          amount: 25,
          entry_spot: 15847.23,
          current_spot: 15832.10,
          profit_loss: 8.75,
          status: 'open',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ];

      setPositions(mockPositions);
      setStats(mockStats);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Set up polling for real-time updates
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleClosePosition = async (positionId: string) => {
    try {
      // Here you would call the API to close the position
      console.log('Closing position:', positionId);
      // Remove the position from the list for now
      setPositions(prev => prev.filter(p => p.id !== positionId));
    } catch (error) {
      console.error('Failed to close position:', error);
    }
  };

  // Mock performance data
  const performanceData = [
    { date: '2025-08-25', value: 1000 },
    { date: '2025-08-26', value: 1050 },
    { date: '2025-08-27', value: 1020 },
    { date: '2025-08-28', value: 1150 },
    { date: '2025-08-29', value: 1180 },
    { date: '2025-08-30', value: 1200 },
    { date: '2025-09-01', value: 1250.50 },
  ];

  return (
    <Layout>
      <div className="flex flex-col gap-8">
        {/* Header */}
        <div className="card-glass m-6">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 p-6">
            <div className="flex-1">
              <h1 className="text-display mb-2">
                Welcome back, {user?.name}! 👋
              </h1>
              <p className="text-body">
                Here's what's happening with your trading today.
              </p>
            </div>
            <div className="flex gap-4 flex-shrink-0">
              <Button
                onClick={fetchData}
                className="btn-secondary"
                disabled={loading}
                leftSection={<IconRefresh size={18} className={loading ? 'animate-spin' : ''} />}
              >
                Refresh
              </Button>
              <Button 
                className="btn-primary"
                leftSection={<IconPlus size={18} />}
              >
                New Trade
              </Button>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="px-4 lg:px-6">
          <StatsGrid stats={stats} loading={loading} />
        </div>

        {/* Dashboard Flexbox Layout */}
        <div className="flex flex-col xl:flex-row gap-8 px-4 lg:px-6 w-full">
          {/* Columna Principal (Chart) */}
          <div className="flex-1 xl:flex-[3]">
            <PerformanceChart 
              data={performanceData} 
              title="Portfolio Performance"
              color={stats?.total_profit && stats.total_profit >= 0 ? 'success' : 'danger'}
            />
          </div>

          {/* Sidebar Derecho (Quick Actions) */}
          <div className="xl:flex-[1] xl:min-w-[320px] flex flex-col gap-6">
            {/* Quick Actions */}
            <div className="card-elevated flex-shrink-0">
              <h3 className="text-headline mb-6">
                Quick Actions
              </h3>
              <div className="flex flex-col gap-3">
                <Button 
                  fullWidth 
                  className="btn-primary flex items-center justify-start gap-3"
                >
                  <IconTrendingUp size={20} />
                  Start AI Trading
                </Button>
                <Button 
                  fullWidth 
                  className="btn-secondary flex items-center justify-start gap-3"
                >
                  <IconTrendingUp size={20} />
                  Market Analysis
                </Button>
                <Button 
                  fullWidth 
                  className="btn-secondary flex items-center justify-start gap-3"
                >
                  <IconTrendingUp size={20} />
                  Parameters
                </Button>
                <Button 
                  fullWidth 
                  className="btn-secondary flex items-center justify-start gap-3"
                >
                  <IconTrendingUp size={20} />
                  Risk Management
                </Button>
              </div>
            </div>

            {/* AI Recommendation */}
            <div className="card flex-shrink-0">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-2xl">🤖</span>
                <h4 className="text-title">AI Recommendation</h4>
              </div>
              <p className="text-body text-sm leading-relaxed mb-4">
                Market conditions are favorable for CALL positions on R_10.
              </p>
              <div className="flex items-center justify-between mb-3">
                <span className="text-caption">Confidence:</span>
                <span className="retro-text-accent font-bold text-lg">78%</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full animate-pulse retro-indicator-turquoise"></div>
                <span className="text-caption">Live Analysis</span>
              </div>
            </div>
          </div>
        </div>

        {/* Active Positions */}
        <div className="mt-12 w-full px-6">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 mb-8">
            <h2 className="text-headline">
              Active Positions ({positions.length})
            </h2>
            <Button className="btn-secondary w-full sm:w-auto flex-shrink-0">
              View All Positions
            </Button>
          </div>

          {positions.length === 0 ? (
            <div className="card-elevated text-center py-16 w-full">
              <div className="w-16 h-16 mx-auto mb-6 rounded-lg flex items-center justify-center retro-icon-turquoise">
                <IconTrendingUp size={32} />
              </div>
              <h3 className="text-title mb-3">
                No active positions
              </h3>
              <p className="text-body mb-8 max-w-md mx-auto">
                Start your first trade to see your positions here. Our AI will help you make informed decisions.
              </p>
              <Button 
                className="btn-primary"
                leftSection={<IconPlus size={20} />}
              >
                Create New Trade
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 w-full">
              {positions.map((position) => (
                <div key={position.id} className="w-full">
                  <TradingCard
                    position={position}
                    onClose={handleClosePosition}
                  />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Activity */}
        <div className="card mt-12 mx-6 mb-6">
          <h3 className="text-headline mb-6">
            Recent Activity
          </h3>
          <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between p-4 border border-retro-brown rounded-lg">
              <div className="flex items-center gap-4">
                <div className="w-3 h-3 rounded-full animate-pulse retro-indicator-turquoise"></div>
                <div className="flex flex-col">
                  <span className="text-body font-medium">
                    Position R_10 CALL closed with 
                    <span className="text-profit ml-1">+$12.50 profit</span>
                  </span>
                </div>
              </div>
              <span className="text-caption">
                2 minutes ago
              </span>
            </div>
            
            <div className="flex items-center justify-between p-4 border border-retro-brown rounded-lg">
              <div className="flex items-center gap-4">
                <div className="w-3 h-3 rounded-full animate-pulse retro-indicator-coral"></div>
                <div className="flex flex-col">
                  <span className="text-body font-medium">
                    New BOOM_1000 PUT position opened
                  </span>
                </div>
              </div>
              <span className="text-caption">
                5 minutes ago
              </span>
            </div>
            
            <div className="flex items-center justify-between p-4 border border-retro-brown rounded-lg">
              <div className="flex items-center gap-4">
                <div className="w-3 h-3 rounded-full animate-pulse retro-indicator-gold"></div>
                <div className="flex flex-col">
                  <span className="text-body font-medium">
                    AI analysis updated market recommendations
                  </span>
                </div>
              </div>
              <span className="text-caption">
                10 minutes ago
              </span>
            </div>
          </div>
        </div>

        {/* Floating Action Button */}
        <div className="fixed bottom-8 right-8 z-50">
          <button 
            className="fab"
            title="Create New Trade"
            aria-label="Create New Trade"
          >
            <IconPlus size={24} />
          </button>
        </div>
      </div>
    </Layout>
  );
}
