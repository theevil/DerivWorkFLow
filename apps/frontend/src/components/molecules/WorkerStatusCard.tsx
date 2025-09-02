/**
 * WorkerStatusCard Molecule - Reusable worker status display
 */

import { ReactNode } from 'react';
import { Group, Text, Stack } from '@mantine/core';
import { RetroCard } from '../atoms/RetroCard';
import { RetroIcon } from '../atoms/RetroIcon';
import { RetroBadge } from '../atoms/RetroBadge';

interface StatusItem {
  label: string;
  value: string | ReactNode;
  variant?: 'success' | 'danger' | 'info';
}

interface WorkerStatusCardProps {
  title: string;
  subtitle?: string;
  icon: ReactNode;
  iconVariant?: 'turquoise' | 'coral' | 'gold';
  status: {
    text: string;
    variant: 'success' | 'danger' | 'warning' | 'info';
  };
  statusItems?: StatusItem[];
  className?: string;
}

export function WorkerStatusCard({
  title,
  subtitle,
  icon,
  iconVariant = 'turquoise',
  status,
  statusItems = [],
  className = '',
}: WorkerStatusCardProps) {
  return (
    <RetroCard
      variant='default'
      padding='md'
      className={`worker-card ${className}`}
    >
      <Group justify='space-between' mb='sm'>
        <Group gap='xs'>
          <RetroIcon variant={iconVariant} size='sm'>
            {icon}
          </RetroIcon>
          <div>
            <Text fw={700} size='sm' className='text-title'>
              {title}
            </Text>
            {subtitle && (
              <Text size='xs' className='text-caption'>
                {subtitle}
              </Text>
            )}
          </div>
        </Group>
        <RetroBadge variant={status.variant} size='xs'>
          {status.text}
        </RetroBadge>
      </Group>

      {statusItems.length > 0 && (
        <Stack gap='xs'>
          {statusItems.map((item, index) => (
            <Group justify='space-between' key={index}>
              <Text size='xs' className='text-caption'>
                {item.label}
              </Text>
              {typeof item.value === 'string' ? (
                item.variant ? (
                  <RetroBadge variant={item.variant} size='xs'>
                    {item.value}
                  </RetroBadge>
                ) : (
                  <Text size='xs' fw={700} className='text-title'>
                    {item.value}
                  </Text>
                )
              ) : (
                item.value
              )}
            </Group>
          ))}
        </Stack>
      )}
    </RetroCard>
  );
}
