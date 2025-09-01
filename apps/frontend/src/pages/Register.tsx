import { TextInput, PasswordInput, Button, Group, Anchor } from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { Link, useNavigate } from 'react-router-dom';
import type { RegisterRequest } from '@deriv-workflow/shared';
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
    <AuthLayout title="Create an account">
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <TextInput
          label="Name"
          placeholder="Your name"
          required
          {...form.getInputProps('name')}
        />
        <TextInput
          label="Email"
          placeholder="your@email.com"
          required
          mt="md"
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
          <Anchor component={Link} to="/login" size="sm">
            Already have an account? Login
          </Anchor>
          <Button type="submit">Register</Button>
        </Group>
      </form>
    </AuthLayout>
  );
}
