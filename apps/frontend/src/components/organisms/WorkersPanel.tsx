/**
 * WorkersPanel Organism - Workers status and controls panel
 */

import { ReactNode } from 'react';
import { Grid, Group, Text } from '@mantine/core';
import { IconRefresh, IconServer } from '@tabler/icons-react';
import { RetroCard } from '../atoms/RetroCard';
import { RetroIcon } from '../atoms/RetroIcon';
import { WorkerStatusCard } from '../molecules/WorkerStatusCard';
import { ActionButtonGroup } from '../molecules/ActionButtonGroup';

export interface WorkerData {
  id: string;
  title: string;
  subtitle?: string;
  icon: ReactNode;
  iconVariant?: 'turquoise' | 'coral' | 'gold';
  status: {
    text: string;
    variant: 'success' | 'danger' | 'warning' | 'info';
  };
  statusItems?: Array<{
    label: string;
    value: string | ReactNode;
    variant?: 'success' | 'danger' | 'info';
  }>;
}

export interface ActionButton {
  label: string;
  icon: ReactNode;
  variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning';
  onClick: () => void;
  disabled?: boolean;
  loading?: boolean;
}

interface WorkersPanelProps {
  workers: WorkerData[];
  quickActions: ActionButton[];
  onRefresh: () => void;
  isRefreshing?: boolean;
  className?: string;
}

export function WorkersPanel({
  workers,
  quickActions,
  onRefresh,
  isRefreshing = false,
  className = ''
}: WorkersPanelProps) {
  return (
    <Grid className={className}>
      {/* Workers Section - 8 columns */}
      <Grid.Col span={{ base: 12, lg: 8 }}>
        <RetroCard variant="default" padding="lg">
          <Group justify="space-between" mb="md">
            <Group gap="sm">
              <RetroIcon variant="turquoise" size="md">
                <IconServer size={18} />
              </RetroIcon>
              <Text fw={700} size="lg" className="text-headline">
                System Workers
              </Text>
            </Group>
            <button 
              className="retro-icon-coral rounded-xl p-2 transition-all hover:scale-110"
              onClick={onRefresh}
              disabled={isRefreshing}
              aria-label="Refresh worker status"
              title="Refresh worker status"
            >
              <IconRefresh size={14} />
            </button>
          </Group>

          <Grid>
            {workers.map((worker) => (
              <Grid.Col key={worker.id} span={{ base: 12, md: 6 }}>
                <WorkerStatusCard
                  title={worker.title}
                  subtitle={worker.subtitle}
                  icon={worker.icon}
                  iconVariant={worker.iconVariant}
                  status={worker.status}
                  statusItems={worker.statusItems}
                />
              </Grid.Col>
            ))}
          </Grid>
        </RetroCard>
      </Grid.Col>

      {/* Quick Actions Section - 4 columns */}
      <Grid.Col span={{ base: 12, lg: 4 }}>
        <RetroCard variant="default" padding="lg">
          <Group justify="space-between" mb="md">
            <Group gap="sm">
              <RetroIcon variant="coral" size="md">
                <IconServer size={18} />
              </RetroIcon>
              <Text fw={700} size="lg" className="text-headline">
                Quick Actions
              </Text>
            </Group>
          </Group>

          <ActionButtonGroup 
            buttons={quickActions}
            direction="vertical"
            spacing="sm"
          />
        </RetroCard>
      </Grid.Col>
    </Grid>
  );
}
