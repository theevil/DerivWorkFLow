import { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Card,
  Text,
  Title,
  Badge,
  Group,
  Stack,
  Button,
  Table,
  ActionIcon,
} from '@mantine/core';
import { IconRefresh, IconTrendingUp, IconTrendingDown } from '@tabler/icons-react';
import type { TradePosition, TradingStats, TradingParametersRequest } from '@deriv-workflow/shared';
import { useAuthStore } from '../stores/auth';
import { api } from '../lib/api';

export function DashboardPage() {
  const user = useAuthStore((state) => state.user);
  const [positions, setPositions] = useState<TradePosition[]>([]);
  const [stats, setStats] = useState<TradingStats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [positionsData, statsData] = await Promise.all([
        api.getPositions(),
        api.getTradingStats(),
      ]);
      setPositions(positionsData);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Set up polling for real-time updates
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open':
        return 'blue';
      case 'closed':
        return 'gray';
      case 'pending':
        return 'yellow';
      default:
        return 'gray';
    }
  };

  const getProfitColor = (profit: number) => {
    return profit >= 0 ? 'green' : 'red';
  };

  return (
    <Container size="xl" py="md">
      <Group justify="space-between" mb="lg">
        <Title order={2}>Trading Dashboard</Title>
        <Group>
          <Text size="sm" c="dimmed">
            Welcome back, {user?.name}
          </Text>
          <ActionIcon variant="light" onClick={fetchData} loading={loading}>
            <IconRefresh size={16} />
          </ActionIcon>
        </Group>
      </Group>

      {/* Stats Cards */}
      <Grid mb="xl">
        <Grid.Col span={{ base: 12, sm: 6, lg: 3 }}>
          <Card withBorder>
            <Stack gap="xs">
              <Text size="sm" c="dimmed">
                Total Profit/Loss
              </Text>
              <Group>
                <Text
                  size="xl"
                  fw={700}
                  c={stats?.total_profit ? getProfitColor(stats.total_profit) : undefined}
                >
                  {stats ? formatCurrency(stats.total_profit) : '--'}
                </Text>
                {stats?.total_profit !== undefined && (
                  <ActionIcon
                    variant="light"
                    color={getProfitColor(stats.total_profit)}
                    size="sm"
                  >
                    {stats.total_profit >= 0 ? (
                      <IconTrendingUp size={16} />
                    ) : (
                      <IconTrendingDown size={16} />
                    )}
                  </ActionIcon>
                )}
              </Group>
            </Stack>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, sm: 6, lg: 3 }}>
          <Card withBorder>
            <Stack gap="xs">
              <Text size="sm" c="dimmed">
                Win Rate
              </Text>
              <Text size="xl" fw={700}>
                {stats ? formatPercentage(stats.win_rate * 100) : '--'}
              </Text>
            </Stack>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, sm: 6, lg: 3 }}>
          <Card withBorder>
            <Stack gap="xs">
              <Text size="sm" c="dimmed">
                Total Trades
              </Text>
              <Text size="xl" fw={700}>
                {stats?.total_trades ?? '--'}
              </Text>
            </Stack>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, sm: 6, lg: 3 }}>
          <Card withBorder>
            <Stack gap="xs">
              <Text size="sm" c="dimmed">
                Average Profit
              </Text>
              <Text size="xl" fw={700}>
                {stats ? formatCurrency(stats.avg_profit) : '--'}
              </Text>
            </Stack>
          </Card>
        </Grid.Col>
      </Grid>

      {/* Active Positions */}
      <Card withBorder mb="xl">
        <Group justify="space-between" mb="md">
          <Title order={3}>Active Positions</Title>
          <Button size="sm">New Trade</Button>
        </Group>

        {positions.length === 0 ? (
          <Text c="dimmed" ta="center" py="xl">
            No active positions
          </Text>
        ) : (
          <Table>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Symbol</Table.Th>
                <Table.Th>Type</Table.Th>
                <Table.Th>Amount</Table.Th>
                <Table.Th>Entry Spot</Table.Th>
                <Table.Th>Current Spot</Table.Th>
                <Table.Th>P&L</Table.Th>
                <Table.Th>Status</Table.Th>
                <Table.Th>Actions</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {positions.map((position) => (
                <Table.Tr key={position.id}>
                  <Table.Td>
                    <Text fw={600}>{position.symbol}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Badge
                      color={position.contract_type === 'CALL' ? 'green' : 'red'}
                      variant="light"
                    >
                      {position.contract_type}
                    </Badge>
                  </Table.Td>
                  <Table.Td>{formatCurrency(position.amount)}</Table.Td>
                  <Table.Td>{position.entry_spot?.toFixed(5) ?? '--'}</Table.Td>
                  <Table.Td>{position.current_spot?.toFixed(5) ?? '--'}</Table.Td>
                  <Table.Td>
                    <Text c={position.profit_loss ? getProfitColor(position.profit_loss) : undefined}>
                      {position.profit_loss ? formatCurrency(position.profit_loss) : '--'}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Badge color={getStatusColor(position.status)} variant="light">
                      {position.status}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    {position.status === 'open' && (
                      <Button size="xs" variant="light" color="red">
                        Close
                      </Button>
                    )}
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        )}
      </Card>

      {/* Recent Activity */}
      <Card withBorder>
        <Title order={3} mb="md">
          Recent Activity
        </Title>
        <Text c="dimmed" ta="center" py="xl">
          Activity feed coming soon...
        </Text>
      </Card>
    </Container>
  );
}
