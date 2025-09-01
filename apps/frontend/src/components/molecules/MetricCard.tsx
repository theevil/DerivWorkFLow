/**
 * MetricCard Molecule - Reusable metric display card
 */

import { ReactNode } from 'react';
import { Group, Text } from '@mantine/core';
import { RetroCard } from '../atoms/RetroCard';
import { RetroIcon } from '../atoms/RetroIcon';
import { RetroBadge } from '../atoms/RetroBadge';

interface MetricCardProps {
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
  className?: string;
}

export function MetricCard({
  title,
  value,
  subtitle,
  icon,
  iconVariant = 'turquoise',
  badge,
  onClick,
  className = ''
}: MetricCardProps) {
  return (
    <RetroCard 
      variant="neumorph" 
      padding="md" 
      onClick={onClick}
      hoverable={!!onClick}
      className={`metric-card ${className}`}
    >
      <Group justify="space-between" mb="xs">
        <RetroIcon variant={iconVariant} size="md">
          {icon}
        </RetroIcon>
        {badge && (
          <RetroBadge variant={badge.variant} size="sm">
            {badge.text}
          </RetroBadge>
        )}
        {!badge && typeof value !== 'object' && (
          <Text size="xl" fw={900} className="text-title">
            {value}
          </Text>
        )}
      </Group>
      
      <Text fw={700} size="sm" mb="xs" className="text-title">
        {title}
      </Text>
      
      {subtitle && (
        <Text size="xs" className="text-caption">
          {subtitle}
        </Text>
      )}
      
      {typeof value === 'object' && (
        <div className="mt-2">
          {value}
        </div>
      )}
    </RetroCard>
  );
}
