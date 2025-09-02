import { TextInput, PasswordInput, Button, Group, Anchor } from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { Link, useNavigate } from 'react-router-dom';
import { IconMail, IconLock, IconSparkles } from '@tabler/icons-react';
import type { LoginRequest } from '../types/trading';
import { AuthLayout } from '../components/AuthLayout';
import { api } from '../lib/api';
import { useAuthStore } from '../stores/auth';

export function LoginPage() {
  const navigate = useNavigate();
  const setAuth = useAuthStore(state => state.setAuth);

  const form = useForm<LoginRequest>({
    initialValues: {
      email: '',
      password: '',
    },
    validate: {
      email: value => (/^\S+@\S+$/.test(value) ? null : 'Invalid email'),
      password: value => (value.length < 6 ? 'Password too short' : null),
    },
  });

  const handleSubmit = async (values: LoginRequest) => {
    try {
      const response = await api.login(values);
      setAuth(response.access_token, response.refresh_token, response.user);
      navigate('/dashboard');
    } catch (error) {
      notifications.show({
        title: 'Error',
        message: error instanceof Error ? error.message : 'Login failed',
        color: 'red',
      });
    }
  };

  return (
    <div className='hero-section'>
      <div className='container mx-auto px-4'>
        <div className='max-w-md mx-auto'>
          {/* Logo y Título */}
          <div className='text-center mb-8 floating'>
            <div
              className='w-20 h-20 mx-auto mb-6 rounded-lg shadow-2xl flex items-center justify-center'
              style={{
                background: 'var(--retro-turquoise)',
                border: '3px solid var(--retro-gold)',
              }}
            >
              <IconSparkles size={32} style={{ color: 'var(--retro-dark)' }} />
            </div>
            <h1 className='text-display mb-2'>Welcome Back!</h1>
            <p className='text-body'>Sign in to your trading account</p>
          </div>

          {/* Formulario */}
          <div className='card-elevated floating-delayed'>
            <form onSubmit={form.onSubmit(handleSubmit)} className='space-y-6'>
              <TextInput
                label='Email Address'
                placeholder='your@email.com'
                required
                leftSection={
                  <IconMail size={20} className='text-retro-brown-400' />
                }
                classNames={{
                  input: 'input-primary',
                  label: 'retro-text-primary font-medium mb-2',
                }}
                {...form.getInputProps('email')}
              />

              <PasswordInput
                label='Password'
                placeholder='Enter your password'
                required
                leftSection={
                  <IconLock size={20} className='text-retro-brown-400' />
                }
                classNames={{
                  input: 'input-primary',
                  label: 'retro-text-primary font-medium mb-2',
                }}
                {...form.getInputProps('password')}
              />

              <Button
                type='submit'
                fullWidth
                size='lg'
                className='btn-primary text-lg font-semibold'
              >
                Sign In
              </Button>

              <div className='text-center'>
                <Anchor
                  component={Link}
                  to='/register'
                  className='retro-text-accent hover:opacity-80 font-medium'
                >
                  Don't have an account? Create one →
                </Anchor>
              </div>
            </form>
          </div>

          {/* Elementos decorativos */}
          <div className='mt-8 text-center'>
            <div className='flex justify-center space-x-4'>
              <div
                className='w-3 h-3 rounded-full animate-pulse'
                style={{ background: 'var(--retro-turquoise)' }}
              ></div>
              <div
                className='w-3 h-3 rounded-full animate-pulse delay-100'
                style={{ background: 'var(--retro-coral)' }}
              ></div>
              <div
                className='w-3 h-3 rounded-full animate-pulse delay-200'
                style={{ background: 'var(--retro-gold)' }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
