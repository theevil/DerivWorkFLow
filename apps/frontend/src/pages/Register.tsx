import { TextInput, PasswordInput, Button, Group, Anchor } from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { Link, useNavigate } from 'react-router-dom';
import { IconUser, IconMail, IconLock, IconRocket } from '@tabler/icons-react';
import type { RegisterRequest } from '../types/trading';
import { AuthLayout } from '../components/AuthLayout';
import { api } from '../lib/api';

export function RegisterPage() {
  const navigate = useNavigate();

  const form = useForm<RegisterRequest>({
    initialValues: {
      email: '',
      password: '',
      name: '',
    },
    validate: {
      email: (value) => (/^\S+@\S+$/.test(value) ? null : 'Invalid email'),
      password: (value) => (value.length < 6 ? 'Password too short' : null),
      name: (value) => (value.length < 2 ? 'Name too short' : null),
    },
  });

  const handleSubmit = async (values: RegisterRequest) => {
    try {
      await api.register(values);
      notifications.show({
        title: 'Success',
        message: 'Registration successful! Please log in.',
        color: 'green',
      });
      navigate('/login');
    } catch (error) {
      notifications.show({
        title: 'Error',
        message: error instanceof Error ? error.message : 'Registration failed',
        color: 'red',
      });
    }
  };

  return (
    <div className="hero-section">
      <div className="container mx-auto px-4">
        <div className="max-w-md mx-auto">
          {/* Logo y Título */}
          <div className="text-center mb-8 floating">
            <div className="w-20 h-20 mx-auto mb-6 rounded-lg shadow-2xl flex items-center justify-center" style={{ background: 'var(--retro-coral)', border: '3px solid var(--retro-gold)' }}>
              <IconRocket size={32} style={{ color: 'var(--retro-cream)' }} />
            </div>
            <h1 className="text-display mb-2">
              Join Us!
            </h1>
            <p className="text-body">
              Create your trading account and start your journey
            </p>
          </div>

          {/* Formulario */}
          <div className="card-elevated floating-delayed">
            <form onSubmit={form.onSubmit(handleSubmit)} className="space-y-6">
              <TextInput
                label="Full Name"
                placeholder="Enter your full name"
                required
                leftSection={<IconUser size={20} className="text-retro-brown-400" />}
                classNames={{
                  input: 'input-primary',
                  label: 'retro-text-primary font-medium mb-2'
                }}
                {...form.getInputProps('name')}
              />

              <TextInput
                label="Email Address"
                placeholder="your@email.com"
                required
                leftSection={<IconMail size={20} className="text-retro-brown-400" />}
                classNames={{
                  input: 'input-primary',
                  label: 'retro-text-primary font-medium mb-2'
                }}
                {...form.getInputProps('email')}
              />

              <PasswordInput
                label="Password"
                placeholder="Create a secure password"
                required
                leftSection={<IconLock size={20} className="text-retro-brown-400" />}
                classNames={{
                  input: 'input-primary',
                  label: 'retro-text-primary font-medium mb-2'
                }}
                {...form.getInputProps('password')}
              />

              <Button 
                type="submit" 
                fullWidth 
                size="lg"
                className="btn-primary text-lg font-semibold"
              >
                Create Account
              </Button>

              <div className="text-center">
                <Anchor 
                  component={Link} 
                  to="/login" 
                  className="text-retro-turquoise-600 hover:text-retro-turquoise-700 font-medium"
                >
                  Already have an account? Sign in →
                </Anchor>
              </div>
            </form>

            {/* Términos y condiciones */}
            <div className="mt-6 p-4 bg-retro-cream-100 rounded-2xl border border-retro-cream-200">
              <p className="text-xs text-retro-brown-600 text-center">
                By creating an account, you agree to our{' '}
                <a href="#" className="text-retro-turquoise-600 hover:underline">Terms of Service</a>
                {' '}and{' '}
                <a href="#" className="text-retro-turquoise-600 hover:underline">Privacy Policy</a>
              </p>
            </div>
          </div>

          {/* Elementos decorativos */}
          <div className="mt-8 text-center">
            <div className="flex justify-center space-x-4 text-retro-brown-400">
              <div className="w-2 h-2 rounded-full bg-retro-coral-400 animate-pulse"></div>
              <div className="w-2 h-2 rounded-full bg-retro-gold-400 animate-pulse delay-100"></div>
              <div className="w-2 h-2 rounded-full bg-retro-turquoise-400 animate-pulse delay-200"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
