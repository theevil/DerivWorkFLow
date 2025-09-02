import React from 'react';
import { Card, Badge, Button } from '@mantine/core';
import {
  IconTrendingUp,
  IconTrendingDown,
  IconX,
  IconEdit,
  IconClock,
} from '@tabler/icons-react';
import type { TradePosition } from '../types/trading';

interface TradingCardProps {
  position: TradePosition;
  onClose?: (positionId: string) => void;
}

export function TradingCard({ position, onClose }: TradingCardProps) {
  const isProfit = (position.profit_loss || 0) >= 0;
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'open':
        return 'badge-success';
      case 'closed':
        return 'badge-info';
      case 'pending':
        return 'badge-warning';
      default:
        return 'badge-info';
    }
  };

  const getSymbolIcon = (symbol: string) => {
    if (symbol.includes('BOOM') || symbol.includes('CRASH')) {
      return '💥';
    }
    if (symbol.includes('R_')) {
      return '📈';
    }
    return '💹';
  };

  return (
    <div className='card-elevated group'>
      {/* Header con símbolo y estado */}
      <div className='flex justify-between items-start mb-6'>
        <div className='flex items-start space-x-3'>
          <div className='w-12 h-12 rounded-2xl bg-gradient-to-br from-retro-turquoise-400 to-retro-coral-400 flex items-center justify-center text-white text-lg font-bold shadow-lg'>
            {getSymbolIcon(position.symbol)}
          </div>
          <div>
            <h3 className='text-title font-bold text-retro-brown-700 mb-1'>
              {position.symbol}
            </h3>
            <div className='flex items-center space-x-2'>
              <span
                className={`badge-${
                  position.contract_type === 'CALL' ? 'success' : 'danger'
                }`}
              >
                {position.contract_type}
              </span>
              <span className={getStatusBadgeClass(position.status)}>
                {position.status.toUpperCase()}
              </span>
            </div>
          </div>
        </div>

        {position.status === 'open' && onClose && (
          <Button
            variant='subtle'
            size='xs'
            onClick={() => onClose(position.id)}
            className='opacity-0 group-hover:opacity-100 transition-opacity duration-200 p-2 rounded-xl hover:bg-retro-red-100 text-retro-red-600'
          >
            <IconX size={16} />
          </Button>
        )}
      </div>

      {/* Grid de información */}
      <div className='grid grid-cols-2 gap-6 mb-6'>
        <div className='neumorph-inset p-4 text-center'>
          <p className='trading-card-label uppercase tracking-wide mb-1'>
            Amount
          </p>
          <p className='trading-card-value'>
            {formatCurrency(position.amount)}
          </p>
        </div>
        <div className='neumorph-inset p-4 text-center'>
          <p className='trading-card-label uppercase tracking-wide mb-1'>
            Entry Spot
          </p>
          <p className='trading-card-value'>
            {position.entry_spot?.toFixed(5) || '--'}
          </p>
        </div>
        <div className='neumorph-inset p-4 text-center'>
          <p className='trading-card-label uppercase tracking-wide mb-1'>
            Current Spot
          </p>
          <p className='trading-card-value'>
            {position.current_spot?.toFixed(5) || '--'}
          </p>
        </div>
        <div className='neumorph-inset p-4 text-center'>
          <p className='trading-card-label uppercase tracking-wide mb-1'>P&L</p>
          <div
            className={`flex items-center justify-center space-x-2 ${
              isProfit ? 'text-profit' : 'text-loss'
            }`}
          >
            {isProfit ? (
              <IconTrendingUp size={18} />
            ) : (
              <IconTrendingDown size={18} />
            )}
            <span className='trading-card-value'>
              {position.profit_loss
                ? formatCurrency(position.profit_loss)
                : '--'}
            </span>
          </div>
        </div>
      </div>

      {/* Footer con acciones */}
      <div className='flex justify-between items-center pt-6 border-t border-retro-cream-200'>
        <div className='flex items-center space-x-2 text-caption text-retro-brown-700'>
          <IconClock size={14} />
          <span>
            {new Date(position.created_at).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>

        {position.status === 'open' && (
          <div className='flex space-x-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200'>
            <Button
              variant='subtle'
              size='xs'
              className='btn-secondary text-xs px-3 py-1 flex items-center'
            >
              <IconEdit size={14} className='mr-1' />
              Edit
            </Button>
            {onClose && (
              <Button
                variant='subtle'
                size='xs'
                onClick={() => onClose(position.id)}
                className='btn-danger text-xs px-3 py-1 flex items-center'
              >
                Close
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Indicador de rendimiento */}
      {isProfit && (
        <div className='absolute top-4 right-4 w-3 h-3 bg-retro-turquoise-400 rounded-full animate-pulse'></div>
      )}
      {!isProfit &&
        position.profit_loss !== undefined &&
        position.profit_loss < 0 && (
          <div className='absolute top-4 right-4 w-3 h-3 bg-retro-red-400 rounded-full animate-pulse'></div>
        )}
    </div>
  );
}
