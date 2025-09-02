/**
 * MetricsGrid Organism - Grid of metric cards in groups of 3
 */

import { ReactNode } from 'react';
import { Grid } from '@mantine/core';
import { MetricCard } from '../molecules/MetricCard';

export interface MetricData {
  id: string;
  title: string;
  value: ReactNode;
  subtitle?: string;
  icon: ReactNode;
  iconVariant?: 'turquoise' | 'coral' | 'gold';
  badge?: {
    text: string;
    variant: 'success' | 'danger' | 'warning' | 'info';
  };
  onClick?: () => void;
}

interface MetricsGridProps {
  metrics: MetricData[];
  className?: string;
}

export function MetricsGrid({ metrics, className = '' }: MetricsGridProps) {
  // Dividir métricas en grupos de 3
  const metricGroups: MetricData[][] = [];
  for (let i = 0; i < metrics.length; i += 3) {
    metricGroups.push(metrics.slice(i, i + 3));
  }

  return (
    <div className={`metrics-grid space-y-6 ${className}`}>
      {metricGroups.map((group, groupIndex) => (
        <Grid key={groupIndex} gutter='lg'>
          {group.map(metric => (
            <Grid.Col
              key={metric.id}
              span={{
                base: 12,
                sm: group.length >= 2 ? 6 : 12,
                md: group.length >= 3 ? 4 : group.length >= 2 ? 6 : 12,
              }}
            >
              <MetricCard
                title={metric.title}
                value={metric.value}
                subtitle={metric.subtitle}
                icon={metric.icon}
                iconVariant={metric.iconVariant}
                badge={metric.badge}
                onClick={metric.onClick}
              />
            </Grid.Col>
          ))}
        </Grid>
      ))}
    </div>
  );
}
