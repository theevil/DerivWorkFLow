import React, { useState } from 'react';
import { Button } from '@mantine/core';
import { 
  IconDashboard, 
  IconChartLine, 
  IconSettings, 
  IconLogout, 
  IconMenu2, 
  IconX,
  IconUser,
  IconBell,
  IconMoon,
  IconSun
} from '@tabler/icons-react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/auth';

interface LayoutProps {
  children: React.ReactNode;
}

interface NavItemProps {
  icon: React.ReactNode;
  label: string;
  href: string;
  active?: boolean;
}

function NavItem({ icon, label, href, active }: NavItemProps) {
  return (
    <Link
      to={href}
      className={`flex items-center space-x-4 px-4 py-3 mx-2 rounded-lg transition-all duration-300 ${
        active
          ? 'card text-retro-brown-700 font-semibold border-2 border-retro-turquoise'
          : 'retro-text-primary hover:bg-retro-cream-100 hover:text-retro-brown-700'
      }`}
    >
      <div className={`transition-colors duration-300 ${
        active ? 'retro-text-accent' : 'retro-text-secondary'
      }`}>
        {icon}
      </div>
      <span className="font-medium">{label}</span>
    </Link>
  );
}

export function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, clearAuth } = useAuthStore();

  const handleLogout = () => {
    clearAuth();
    navigate('/login');
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    // Here you would typically update the theme context or localStorage
  };

  const navItems = [
    {
      icon: <IconDashboard size={20} />,
      label: 'Dashboard',
      href: '/dashboard',
    },
    {
      icon: <IconChartLine size={20} />,
      label: 'Trading',
      href: '/trading',
    },
    {
      icon: <IconSettings size={20} />,
      label: 'Settings',
      href: '/settings',
    },
  ];

  return (
    <div className={`min-h-screen retro-bg-primary flex ${darkMode ? 'dark' : ''}`}>
      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-72 bg-surface-secondary border-r-2 border-retro-brown flex flex-col ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      } lg:translate-x-0`}>
        
        {/* Header del Sidebar */}
        <div className="flex items-center justify-between h-20 px-6 border-b-2 border-retro-brown flex-shrink-0">
          <h1 className="text-xl font-bold retro-text-secondary">
            Deriv Workflow
          </h1>
          <Button
            variant="subtle"
            size="sm"
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-2 rounded-xl hover:bg-retro-cream-100"
          >
            <IconX size={20} />
          </Button>
        </div>

        {/* Navegación con Scroll */}
        <div className="flex-1 overflow-y-auto py-6 sidebar-scroll">
          <nav className="px-4 space-y-2">
            {navItems.map((item) => (
              <NavItem
                key={item.href}
                icon={item.icon}
                label={item.label}
                href={item.href}
                active={location.pathname === item.href}
              />
            ))}
          </nav>
          
          {/* Espaciador para más opciones */}
          <div className="px-6 mt-8 space-y-4">
            <div className="border-t-2 border-retro-brown pt-4">
              <h3 className="text-sm font-semibold retro-text-secondary mb-3 uppercase tracking-wide">
                Quick Tools
              </h3>
              <div className="space-y-2">
                <button className="w-full text-left px-4 py-2 rounded-lg retro-text-primary hover:bg-retro-cream-100 transition-colors">
                  Market Analysis
                </button>
                <button className="w-full text-left px-4 py-2 rounded-lg retro-text-primary hover:bg-retro-cream-100 transition-colors">
                  Risk Calculator
                </button>
                <button className="w-full text-left px-4 py-2 rounded-lg retro-text-primary hover:bg-retro-cream-100 transition-colors">
                  Trade History
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* User Info - Fixed at Bottom */}
        <div className="flex-shrink-0 p-4 border-t-2 border-retro-brown">
          <div className="card p-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg retro-icon-turquoise flex items-center justify-center flex-shrink-0">
                <IconUser size={18} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-bold retro-text-primary truncate">
                  {user?.name}
                </p>
                <p className="text-xs retro-text-secondary truncate">
                  {user?.email}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <div className="flex flex-col min-h-screen main-content lg:ml-72 w-full">
        {/* Top header - Fixed */}
        <header className="flex-shrink-0 glass-effect border-b-2 border-retro-brown sticky top-0 z-40 w-full">
          <div className="flex items-center justify-between h-20 px-8 w-full">
            <div className="flex items-center space-x-6">
              <Button
                variant="subtle"
                size="sm"
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-3 rounded-2xl hover:bg-retro-cream-100"
              >
                <IconMenu2 size={20} />
              </Button>
              <h2 className="text-2xl font-bold text-retro-brown-700">
                {navItems.find(item => item.href === location.pathname)?.label || 'Dashboard'}
              </h2>
            </div>

            <div className="flex items-center space-x-4">
              {/* Notifications */}
              <Button 
                variant="subtle" 
                className="relative p-3 rounded-2xl hover:bg-retro-cream-100 text-retro-brown-600"
              >
                <IconBell size={20} />
                <span className="absolute -top-1 -right-1 h-3 w-3 bg-retro-red-500 rounded-full animate-pulse"></span>
              </Button>

              {/* Dark mode toggle */}
              <Button 
                variant="subtle" 
                onClick={toggleDarkMode}
                className="p-3 rounded-2xl hover:bg-retro-cream-100 text-retro-brown-600"
              >
                {darkMode ? <IconSun size={20} /> : <IconMoon size={20} />}
              </Button>

              {/* User menu */}
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-br from-retro-turquoise-400 to-retro-coral-400 rounded-2xl flex items-center justify-center">
                  <IconUser size={16} className="text-white" />
                </div>
                <span className="hidden md:block text-sm font-medium text-retro-brown-700">
                  {user?.name}
                </span>
                <Button 
                  variant="subtle" 
                  size="sm"
                  onClick={handleLogout}
                  className="p-2 rounded-xl hover:bg-retro-cream-100 text-retro-brown-500"
                >
                  <IconLogout size={16} />
                </Button>
              </div>
            </div>
          </div>
        </header>

        {/* Page content - Scrollable */}
        <main className="flex-1 overflow-y-auto w-full">
          <div className="w-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
