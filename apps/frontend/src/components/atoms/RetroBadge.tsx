/**
 * RetroBadge Atom - Reusable badge component with retro styling
 */

import { ReactNode } from 'react';

interface RetroBadgeProps {
  children: ReactNode;
  variant?: 'success' | 'danger' | 'warning' | 'info';
  size?: 'xs' | 'sm' | 'md' | 'lg';
  className?: string;
}

export function RetroBadge({
  children,
  variant = 'info',
  size = 'sm',
  className = ''
}: RetroBadgeProps) {
  const baseClasses = 'inline-flex items-center rounded-full font-semibold border';
  
  const variantClasses = {
    success: 'badge-success',
    danger: 'badge-danger',
    warning: 'badge-warning',
    info: 'badge-info'
  };

  const sizeClasses = {
    xs: 'px-2 py-1 text-xs',
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-5 py-2.5 text-lg'
  };

  return (
    <span className={`
      ${baseClasses}
      ${variantClasses[variant]}
      ${sizeClasses[size]}
      ${className}
    `}>
      {children}
    </span>
  );
}
