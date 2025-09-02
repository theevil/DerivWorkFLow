/**
 * Layout Component - Refactored to use AppLayout template
 */

import React from 'react';
import { AppLayout } from './templates/AppLayout';

interface LayoutProps {
  children: React.ReactNode;
}

export function LayoutRefactored({ children }: LayoutProps) {
  return <AppLayout>{children}</AppLayout>;
}
