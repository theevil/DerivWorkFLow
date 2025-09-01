import React from 'react';
import { IconTrendingUp, IconTrendingDown, IconTarget, IconUsers } from '@tabler/icons-react';
import type { TradingStats } from '../types/trading';

interface StatsGridProps {
  stats: TradingStats | null;
  loading?: boolean;
}

interface StatCardProps {
  title: string;
  value: string;
  change?: string;
  icon: React.ReactNode;
  color: 'success' | 'danger' | 'warning' | 'info';
}

function StatCard({ title, value, change, icon, color }: StatCardProps) {
  const colorClasses = {
    success: 'bg-success-50 text-success-600 border-success-200',
    danger: 'bg-danger-50 text-danger-600 border-danger-200',
    warning: 'bg-warning-50 text-warning-600 border-warning-200',
    info: 'bg-primary-50 text-primary-600 border-primary-200',
  };

  return (
    <div className="card bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6 transition-all duration-200 hover:shadow-xl">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">
            {title}
          </p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">
            {value}
          </p>
          {change && (
            <p className={`text-sm mt-1 ${change.startsWith('+') ? 'text-success-600' : 'text-danger-600'}`}>
              {change}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

export function StatsGrid({ stats, loading = false }: StatsGridProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(2)}%`;
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="card animate-pulse">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded mb-2"></div>
                <div className="h-8 bg-gray-200 rounded"></div>
              </div>
              <div className="w-12 h-12 bg-gray-200 rounded-lg"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total P&L"
          value="--"
          icon={<IconTrendingUp size={24} />}
          color="info"
        />
        <StatCard
          title="Win Rate"
          value="--"
          icon={<IconTarget size={24} />}
          color="info"
        />
        <StatCard
          title="Total Trades"
          value="--"
          icon={<IconUsers size={24} />}
          color="info"
        />
        <StatCard
          title="Average Profit"
          value="--"
          icon={<IconTrendingUp size={24} />}
          color="info"
        />
      </div>
    );
  }

  const isProfitable = stats.total_profit >= 0;
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <StatCard
        title="Total P&L"
        value={formatCurrency(stats.total_profit)}
        change={isProfitable ? '+' + formatPercentage(Math.abs(stats.total_profit) / 1000) : '-' + formatPercentage(Math.abs(stats.total_profit) / 1000)}
        icon={isProfitable ? <IconTrendingUp size={24} /> : <IconTrendingDown size={24} />}
        color={isProfitable ? 'success' : 'danger'}
      />
      
      <StatCard
        title="Win Rate"
        value={formatPercentage(stats.win_rate * 100)}
        icon={<IconTarget size={24} />}
        color={stats.win_rate > 0.5 ? 'success' : stats.win_rate > 0.3 ? 'warning' : 'danger'}
      />
      
      <StatCard
        title="Total Trades"
        value={stats.total_trades.toString()}
        icon={<IconUsers size={24} />}
        color="info"
      />
      
      <StatCard
        title="Average Profit"
        value={formatCurrency(stats.avg_profit)}
        icon={stats.avg_profit >= 0 ? <IconTrendingUp size={24} /> : <IconTrendingDown size={24} />}
        color={stats.avg_profit >= 0 ? 'success' : 'danger'}
      />
    </div>
  );
}
