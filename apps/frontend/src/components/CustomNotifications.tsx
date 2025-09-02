import React from 'react';
import { Notifications } from '@mantine/notifications';

export function CustomNotifications() {
  return (
    <div style={{ position: 'relative', zIndex: 1000 }}>
      <Notifications 
        position="top-right"
        zIndex={1000}
        containerWidth={400}
        autoClose={5000}
        limit={5}
        styles={{
          root: {
            position: 'fixed',
            top: '20px',
            right: '20px',
            left: 'auto',
            bottom: 'auto',
            zIndex: 1000,
            maxWidth: '400px',
            overflow: 'visible',
          },
          notification: {
            marginBottom: '10px',
            borderRadius: '12px',
            border: '2px solid',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          },
          title: {
            fontWeight: 600,
            fontSize: '14px',
          },
          description: {
            fontSize: '13px',
            lineHeight: 1.4,
          },
        }}
      />
    </div>
  );
}
