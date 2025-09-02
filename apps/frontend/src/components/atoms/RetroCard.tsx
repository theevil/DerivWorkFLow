/**
 * RetroCard Atom - Reusable card component with retro styling
 */

import { ReactNode } from 'react';

interface RetroCardProps {
  children: ReactNode;
  variant?: 'default' | 'elevated' | 'glass' | 'neumorph';
  padding?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  onClick?: () => void;
  hoverable?: boolean;
}

export function RetroCard({
  children,
  variant = 'default',
  padding = 'md',
  className = '',
  onClick,
  hoverable = false,
}: RetroCardProps) {
  const baseClasses = 'rounded-2xl transition-all duration-300';

  const variantClasses = {
    default: 'card',
    elevated: 'card-elevated',
    glass: 'card-glass',
    neumorph: 'neumorph-inset',
  };

  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
    xl: 'p-10',
  };

  const interactiveClasses =
    onClick || hoverable
      ? 'cursor-pointer hover:shadow-xl hover:-translate-y-2'
      : '';

  return (
    <div
      onClick={onClick}
      className={`
        ${baseClasses}
        ${variantClasses[variant]}
        ${paddingClasses[padding]}
        ${interactiveClasses}
        ${className}
      `}
    >
      {children}
    </div>
  );
}
