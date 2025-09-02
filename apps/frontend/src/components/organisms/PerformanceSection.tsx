/**
 * PerformanceSection Organism - Trading performance analytics
 */

import { ReactNode } from 'react';
import { Grid, Group, Text, Box } from '@mantine/core';
import { NumberFormatter } from '@mantine/core';
import { IconChartLine } from '@tabler/icons-react';
import { RetroCard } from '../atoms/RetroCard';
import { RetroIcon } from '../atoms/RetroIcon';
import { RetroBadge } from '../atoms/RetroBadge';
import { RetroButton } from '../atoms/RetroButton';
import { MetricsGrid, MetricData } from './MetricsGrid';

export interface PerformanceData {
  trading_stats: {
    total_trades: number;
    win_rate: number;
    avg_profit: number;
    profitable_trades: number;
    max_profit: number;
    min_profit: number;
    total_profit: number;
  };
}

interface PerformanceSectionProps {
  performance: PerformanceData;
  onViewReport?: () => void;
  className?: string;
}

export function PerformanceSection({
  performance,
  onViewReport,
  className = '',
}: PerformanceSectionProps) {
  // Preparar métricas para el grid
  const performanceMetrics: MetricData[] = [
    {
      id: 'total-trades',
      title: 'Total Trades',
      value: performance.trading_stats.total_trades,
      subtitle: 'Automated + Manual',
      icon: <IconChartLine size={20} />,
      iconVariant: 'turquoise',
    },
    {
      id: 'win-rate',
      title: 'Win Rate',
      value: (
        <Group gap='xs'>
          <Text size='2xl' fw={900} className='text-title'>
            <NumberFormatter
              value={performance.trading_stats.win_rate * 100}
              decimalScale={1}
              suffix='%'
            />
          </Text>
          <div className='w-10 h-10 rounded-full border-4 border-retro-turquoise-400 flex items-center justify-center'>
            <Text fw={600} ta='center' size='xs' className='text-title'>
              ✓
            </Text>
          </div>
        </Group>
      ),
      subtitle: 'Success ratio',
      icon: <IconChartLine size={20} />,
      iconVariant: 'turquoise',
    },
    {
      id: 'avg-profit',
      title: 'Avg Profit',
      value: (
        <NumberFormatter
          value={performance.trading_stats.avg_profit}
          thousandSeparator
          decimalScale={2}
          prefix='$'
        />
      ),
      subtitle: 'Per trade',
      icon: <IconChartLine size={20} />,
      iconVariant:
        performance.trading_stats.avg_profit > 0 ? 'turquoise' : 'coral',
    },
  ];

  return (
    <RetroCard variant='elevated' padding='xl' className={className}>
      <Group justify='space-between' mb='lg'>
        <Group gap='md'>
          <RetroIcon variant='turquoise' size='lg'>
            <IconChartLine size={28} />
          </RetroIcon>
          <Box>
            <Text fw={700} size='xl' className='text-headline'>
              Performance Analytics
            </Text>
            <Text size='sm' className='text-caption'>
              7-day trading performance overview
            </Text>
          </Box>
        </Group>
        <RetroBadge variant='info' size='md'>
          Last 7 days
        </RetroBadge>
      </Group>

      {/* Performance Metrics Grid */}
      <MetricsGrid metrics={performanceMetrics} />

      {/* Summary Stats */}
      <div className='border-t-2 border-retro-brown mt-6 pt-6'>
        <Group justify='space-between'>
          <Group gap='lg'>
            <Box ta='center'>
              <Text size='sm' className='text-caption' mb='xs'>
                Max Profit
              </Text>
              <Text fw={700} className='text-profit'>
                <NumberFormatter
                  value={performance.trading_stats.max_profit}
                  thousandSeparator
                  decimalScale={2}
                  prefix='$'
                />
              </Text>
            </Box>

            <Box ta='center'>
              <Text size='sm' className='text-caption' mb='xs'>
                Max Loss
              </Text>
              <Text fw={700} className='text-loss'>
                <NumberFormatter
                  value={performance.trading_stats.min_profit}
                  thousandSeparator
                  decimalScale={2}
                  prefix='$'
                />
              </Text>
            </Box>

            <Box ta='center'>
              <Text size='sm' className='text-caption' mb='xs'>
                Total P&L
              </Text>
              <Text
                fw={700}
                className={`text-${
                  performance.trading_stats.total_profit > 0 ? 'profit' : 'loss'
                }`}
              >
                <NumberFormatter
                  value={performance.trading_stats.total_profit}
                  thousandSeparator
                  decimalScale={2}
                  prefix='$'
                />
              </Text>
            </Box>
          </Group>

          {onViewReport && (
            <RetroButton
              variant='primary'
              leftIcon={<IconChartLine size={16} />}
              onClick={onViewReport}
            >
              View Detailed Report
            </RetroButton>
          )}
        </Group>
      </div>
    </RetroCard>
  );
}
