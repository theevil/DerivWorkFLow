/**
 * ActionButtonGroup Molecule - Group of action buttons
 */

import { ReactNode } from 'react';
import { Stack } from '@mantine/core';
import { RetroButton } from '../atoms/RetroButton';

interface ActionButton {
  label: string;
  icon: ReactNode;
  variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning';
  onClick: () => void;
  disabled?: boolean;
  loading?: boolean;
}

interface ActionButtonGroupProps {
  title?: string;
  buttons: ActionButton[];
  direction?: 'vertical' | 'horizontal';
  spacing?: 'xs' | 'sm' | 'md' | 'lg';
  className?: string;
}

export function ActionButtonGroup({
  buttons,
  direction = 'vertical',
  spacing = 'sm',
  className = '',
}: ActionButtonGroupProps) {
  if (direction === 'horizontal') {
    return (
      <div className={`flex gap-${spacing} ${className}`}>
        {buttons.map((button, index) => (
          <RetroButton
            key={index}
            variant={button.variant || 'primary'}
            leftIcon={button.icon}
            onClick={button.onClick}
            disabled={button.disabled}
            loading={button.loading}
            fullWidth
            size='sm'
          >
            {button.label}
          </RetroButton>
        ))}
      </div>
    );
  }

  return (
    <Stack gap={spacing} className={className}>
      {buttons.map((button, index) => (
        <RetroButton
          key={index}
          variant={button.variant || 'primary'}
          leftIcon={button.icon}
          onClick={button.onClick}
          disabled={button.disabled}
          loading={button.loading}
          fullWidth
          size='sm'
        >
          {button.label}
        </RetroButton>
      ))}
    </Stack>
  );
}
