/**
 * Sidebar Organism Component - Reusable navigation sidebar
 */

import { Button } from '@mantine/core';
import { 
  IconDashboard, 
  IconChartLine, 
  IconSettings, 
  IconRobot,
  IconX,
  IconUser,
  IconAnalyze,
  IconCalculator,
  IconHistory,
  IconTrendingUp,
  IconShield,
  IconTarget,
  IconLogout
} from '@tabler/icons-react';
import { Link, useLocation } from 'react-router-dom';

interface NavItem {
  icon: React.ReactNode;
  label: string;
  href: string;
}

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  user?: {
    name: string;
    email?: string;
  };
  onLogout: () => void;
}

interface NavItemProps {
  icon: React.ReactNode;
  label: string;
  href: string;
  active: boolean;
}

function NavItem({ icon, label, href, active }: NavItemProps) {
  return (
    <Link
      to={href}
      className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${
        active
          ? 'retro-bg-secondary-solid border-2 border-retro-turquoise retro-text-accent shadow-lg'
          : 'hover:bg-retro-cream-100 retro-text-primary hover:retro-text-accent hover:translate-x-2'
      }`}
    >
      <span className={`transition-transform duration-200 ${active ? 'text-retro-turquoise' : 'group-hover:scale-110'}`}>
        {icon}
      </span>
      <span className="font-medium">{label}</span>
    </Link>
  );
}

export function Sidebar({ isOpen, onClose, user, onLogout }: SidebarProps) {
  const location = useLocation();

  const navItems: NavItem[] = [
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
      icon: <IconRobot size={20} />,
      label: 'Automation',
      href: '/automation',
    },
    {
      icon: <IconSettings size={20} />,
      label: 'Settings',
      href: '/settings',
    },
  ];

  const quickTools = [
    { icon: <IconAnalyze size={18} />, label: 'Market Analysis' },
    { icon: <IconCalculator size={18} />, label: 'Risk Calculator' },
    { icon: <IconHistory size={18} />, label: 'Trade History' },
    { icon: <IconTrendingUp size={18} />, label: 'Performance' },
    { icon: <IconShield size={18} />, label: 'Risk Management' },
    { icon: <IconTarget size={18} />, label: 'Trading Goals' },
  ];

  return (
    <div className={`fixed inset-y-0 left-0 z-50 w-72 border-r-2 border-retro-brown flex flex-col backdrop-blur-xl bg-black/20 transition-transform duration-300 ${
      isOpen ? 'translate-x-0' : '-translate-x-full'
    } lg:translate-x-0`}>
      
      {/* Header del Sidebar */}
      <div className="flex items-center justify-between h-20 px-6 border-b-2 border-retro-brown flex-shrink-0">
        <h1 className="text-xl font-bold retro-text-secondary">
          Deriv Workflow
        </h1>
        <Button
          variant="subtle"
          size="sm"
          onClick={onClose}
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
        
        {/* Quick Tools Section */}
        <div className="px-6 mt-8 space-y-4">
          <div className="border-t-2 border-retro-brown pt-4">
            <h3 className="text-sm font-semibold retro-text-secondary mb-3 uppercase tracking-wide">
              Quick Tools
            </h3>
            <div className="space-y-2">
              {quickTools.map((tool) => (
                <button 
                  key={tool.label}
                  className="w-full text-left px-4 py-3 rounded-lg retro-text-primary hover:bg-retro-cream-100 transition-colors flex items-center gap-3"
                >
                  <span className="retro-text-accent">{tool.icon}</span>
                  {tool.label}
                </button>
              ))}
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
            <div className="min-w-0 flex-1">
              <p className="text-sm font-semibold text-title truncate">
                {user?.name || 'Usuario'}
              </p>
              <p className="text-xs text-caption truncate">
                {user?.email || 'usuario@example.com'}
              </p>
            </div>
            <button
              onClick={onLogout}
              className="retro-icon-coral rounded-lg p-2 transition-all hover:scale-110"
              aria-label="Cerrar sesión"
              title="Cerrar sesión"
            >
              <IconLogout size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
