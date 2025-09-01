import { TextInput, PasswordInput, Button, Group, Anchor } from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { Link, useNavigate } from 'react-router-dom';
import type { LoginRequest } from '@deriv-workflow/shared';
import { AuthLayout } from '../components/AuthLayout';
import { api } from '../lib/api';
import { useAuthStore } from '../stores/auth';

export function LoginPage() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);

  const form = useForm<LoginRequest>({
    initialValues: {
      email: '',
      password: '',
    },
    validate: {
      email: (value) => (/^\S+@\S+$/.test(value) ? null : 'Invalid email'),
      password: (value) => (value.length < 6 ? 'Password too short' : null),
    },
  });

  const handleSubmit = async (values: LoginRequest) => {
    try {
      const response = await api.login(values);
      setAuth(response.access_token, response.user);
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
    <AuthLayout title="Welcome back!">
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <TextInput
          label="Email"
          placeholder="your@email.com"
          required
          {...form.getInputProps('email')}
        />
        <PasswordInput
          label="Password"
          placeholder="Your password"
          required
          mt="md"
          {...form.getInputProps('password')}
        />
        <Group justify="space-between" mt="lg">
          <Anchor component={Link} to="/register" size="sm">
            Don't have an account? Register
          </Anchor>
          <Button type="submit">Sign in</Button>
        </Group>
      </form>
    </AuthLayout>
  );
}
