/**
 * AppLayout Template - Main application layout with sidebar
 */

import React, { useState } from 'react';
import { Button, Group, ActionIcon, Text, Box, Tooltip } from '@mantine/core';
import {
  IconMenu2,
  IconBell,
  IconSun,
  IconMoon,
  IconUser,
  IconLogout,
} from '@tabler/icons-react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores/auth';
import { useAutomationStore } from '../../stores/automation';
import { useAutomationWebSocket } from '../../hooks/useAutomationWebSocket';
import { Sidebar } from '../organisms/Sidebar';

interface AppLayoutProps {
  children: React.ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, clearAuth } = useAuthStore();

  // Automation state for notifications
  const { unacknowledgedCount } = useAutomationStore();
  const { isConnected } = useAutomationWebSocket({ enabled: true });

  const handleLogout = () => {
    clearAuth();
    navigate('/login');
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    // Here you would typically update the theme context or localStorage
  };

  // Obtener el título de la página actual
  const getPageTitle = () => {
    switch (location.pathname) {
      case '/dashboard':
        return 'Dashboard';
      case '/trading':
        return 'Trading';
      case '/automation':
        return 'Automation';
      case '/settings':
        return 'Settings';
      default:
        return 'Dashboard';
    }
  };

  return (
    <div
      className={`min-h-screen retro-bg-primary flex ${darkMode ? 'dark' : ''}`}
    >
      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        user={user}
        onLogout={handleLogout}
      />

      {/* Overlay para móvil */}
      {sidebarOpen && (
        <div
          className='fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden'
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <div className='flex flex-col min-h-screen main-content lg:ml-72 w-full'>
        {/* Top header - Fixed */}
        <header className='flex-shrink-0 glass-effect border-b-2 border-retro-brown sticky top-0 z-40 w-full'>
          <div className='flex items-center justify-between h-20 px-8 w-full'>
            <div className='flex items-center space-x-6'>
              <Button
                variant='subtle'
                size='sm'
                onClick={() => setSidebarOpen(true)}
                className='lg:hidden p-3 rounded-2xl hover:bg-retro-cream-100'
              >
                <IconMenu2 size={20} />
              </Button>
              <h2 className='text-2xl font-bold text-retro-brown-700'>
                {getPageTitle()}
              </h2>
            </div>

            <div className='flex items-center space-x-4'>
              {/* Notifications */}
              <Tooltip label='View notifications'>
                <Button
                  variant='subtle'
                  component={Link}
                  to='/automation'
                  className='relative p-3 rounded-2xl hover:bg-retro-cream-100 text-retro-brown-600'
                >
                  <IconBell size={20} />
                  {unacknowledgedCount > 0 && (
                    <span className='absolute -top-1 -right-1 h-4 w-4 bg-retro-red-500 text-white text-xs rounded-full flex items-center justify-center animate-pulse'>
                      {unacknowledgedCount > 9 ? '9+' : unacknowledgedCount}
                    </span>
                  )}
                  {!isConnected && (
                    <span className='absolute -bottom-1 -right-1 h-2 w-2 bg-yellow-500 rounded-full'></span>
                  )}
                </Button>
              </Tooltip>

              {/* Dark mode toggle */}
              <Tooltip label='Toggle theme'>
                <Button
                  variant='subtle'
                  onClick={toggleDarkMode}
                  className='p-3 rounded-2xl hover:bg-retro-cream-100 text-retro-brown-600'
                >
                  {darkMode ? <IconSun size={20} /> : <IconMoon size={20} />}
                </Button>
              </Tooltip>

              {/* User menu */}
              <div className='flex items-center space-x-3'>
                <div className='w-8 h-8 bg-gradient-to-br from-retro-turquoise-400 to-retro-coral-400 rounded-2xl flex items-center justify-center'>
                  <IconUser size={16} className='text-white' />
                </div>
                <span className='hidden md:block text-sm font-medium text-retro-brown-700'>
                  {user?.name}
                </span>
                <Tooltip label='Logout'>
                  <Button
                    variant='subtle'
                    size='sm'
                    onClick={handleLogout}
                    className='p-2 rounded-xl hover:bg-retro-cream-100 text-retro-brown-500'
                  >
                    <IconLogout size={16} />
                  </Button>
                </Tooltip>
              </div>
            </div>
          </div>
        </header>

        {/* Page content - Scrollable */}
        <main className='flex-1 overflow-y-auto w-full'>
          <div className='w-full'>{children}</div>
        </main>
      </div>
    </div>
  );
}
