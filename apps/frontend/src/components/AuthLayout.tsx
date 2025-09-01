import { Container, Paper, Title } from '@mantine/core';
import { ReactNode } from 'react';

interface AuthLayoutProps {
  children: ReactNode;
  title: string;
}

export function AuthLayout({ children, title }: AuthLayoutProps) {
  return (
    <Container size={420} my={40}>
      <Title ta="center" mb={30}>
        {title}
      </Title>
      <Paper withBorder radius="md" p={30}>
        {children}
      </Paper>
    </Container>
  );
}
