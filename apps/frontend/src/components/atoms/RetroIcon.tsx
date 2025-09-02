/**
 * RetroIcon Atom - Reusable icon wrapper with retro styling
 */

import { ReactNode } from 'react';

interface RetroIconProps {
  children: ReactNode;
  variant?: 'turquoise' | 'coral' | 'gold';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

export function RetroIcon({
  children,
  variant = 'turquoise',
  size = 'md',
  className = '',
}: RetroIconProps) {
  const baseClasses =
    'retro-icon flex items-center justify-center rounded-xl transition-all';

  const variantClasses = {
    turquoise: 'retro-icon-turquoise',
    coral: 'retro-icon-coral',
    gold: 'bg-retro-gold border-3 border-retro-brown color-retro-dark',
  };

  const sizeClasses = {
    sm: 'p-1',
    md: 'p-2',
    lg: 'p-3',
    xl: 'p-4',
  };

  return (
    <div
      className={`
      ${baseClasses}
      ${variantClasses[variant]}
      ${sizeClasses[size]}
      ${className}
    `}
    >
      {children}
    </div>
  );
}
