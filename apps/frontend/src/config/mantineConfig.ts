import { MantineThemeOverride } from '@mantine/core';

export const mantineConfig: MantineThemeOverride = {
  colorScheme: 'light',
  primaryColor: 'teal',
  fontFamily: 'Inter, Space Grotesk, system-ui, sans-serif',
  components: {
    Notifications: {
      styles: {
        root: {
          position: 'fixed',
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
      },
      defaultProps: {
        position: 'top-right',
        zIndex: 1000,
        containerWidth: 400,
        autoClose: 5000,
        limit: 5,
      },
    },
    Portal: {
      styles: {
        root: {
          position: 'fixed',
          zIndex: 999,
          pointerEvents: 'none',
        },
      },
    },
    Modal: {
      styles: {
        root: {
          zIndex: 1001,
        },
        overlay: {
          zIndex: 1000,
        },
      },
    },
    Tooltip: {
      styles: {
        tooltip: {
          zIndex: 1002,
        },
      },
    },
    Popover: {
      styles: {
        dropdown: {
          zIndex: 1002,
        },
      },
    },
  },
  globalStyles: (theme) => ({
    'body': {
      overflowX: 'hidden',
    },
    '#root': {
      overflowX: 'hidden',
      position: 'relative',
    },
    '.mantine-Notifications-root': {
      position: 'fixed !important',
      zIndex: '1000 !important',
      maxWidth: '400px !important',
      overflow: 'visible !important',
    },
    '.mantine-Notifications-root[data-position="bottom-left"], .mantine-Notifications-root[data-position="bottom-center"]': {
      bottom: '20px !important',
      left: '20px !important',
      right: 'auto !important',
      top: 'auto !important',
    },
    '.mantine-Notifications-root[data-position="top-right"]': {
      top: '20px !important',
      right: '20px !important',
      left: 'auto !important',
      bottom: 'auto !important',
    },
    'protonpass-root, [data-protonpass-role="root"]': {
      display: 'none !important',
      visibility: 'hidden !important',
      position: 'absolute !important',
      left: '-9999px !important',
      top: '-9999px !important',
      zIndex: '-1 !important',
    },
    'div[data-portal="true"]': {
      position: 'fixed !important',
      zIndex: '999 !important',
      pointerEvents: 'none !important',
    },
    'div[data-portal="true"]:empty': {
      display: 'none !important',
    },
  }),
};
