import React from 'react';
import { MantineProvider } from '@mantine/core';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from './pages/Login';
import { RegisterPage } from './pages/Register';
import { DashboardPage } from './pages/Dashboard';
import { TradingPage } from './pages/Trading';
import { Automation } from './pages/Automation';
import { SettingsPage } from './pages/Settings';
import { useAuthStore } from './stores/auth';
import { CustomNotifications } from './components/CustomNotifications';
import { cleanupProblematicElements } from './utils/domCleanup';
import { mantineConfig } from './config/mantineConfig';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);
  return isAuthenticated ? children : <Navigate to='/login' />;
}

export function App() {
  const { initializeAuth } = useAuthStore();

  // Initialize authentication on app start
  React.useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  // Clean up problematic DOM elements
  React.useEffect(() => {
    cleanupProblematicElements();
  }, []);

  return (
    <MantineProvider theme={mantineConfig}>
      <CustomNotifications />
      <BrowserRouter>
        <Routes>
          <Route path='/login' element={<LoginPage />} />
          <Route path='/register' element={<RegisterPage />} />
          <Route
            path='/dashboard'
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path='/trading'
            element={
              <ProtectedRoute>
                <TradingPage />
              </ProtectedRoute>
            }
          />
          <Route
            path='/automation'
            element={
              <ProtectedRoute>
                <Automation />
              </ProtectedRoute>
            }
          />
          <Route
            path='/settings'
            element={
              <ProtectedRoute>
                <SettingsPage />
              </ProtectedRoute>
            }
          />
          <Route path='/' element={<Navigate to='/dashboard' replace />} />
        </Routes>
      </BrowserRouter>
    </MantineProvider>
  );
}
