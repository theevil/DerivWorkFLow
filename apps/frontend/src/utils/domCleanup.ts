/**
 * Utility to clean up problematic DOM elements that cause visual errors
 */

export function cleanupProblematicElements() {
  // Remove ProtonPass extension elements
  const protonPassElements = document.querySelectorAll('protonpass-root, [data-protonpass-role="root"]');
  protonPassElements.forEach(element => {
    element.remove();
  });

  // Fix Mantine notification containers
  const notificationContainers = document.querySelectorAll('.mantine-Notifications-root');
  notificationContainers.forEach(container => {
    const element = container as HTMLElement;
    element.style.position = 'fixed';
    element.style.zIndex = '1000';
    element.style.maxWidth = '400px';
    element.style.overflow = 'visible';
    
    // Ensure proper positioning
    const position = element.getAttribute('data-position');
    if (position === 'bottom-left' || position === 'bottom-center') {
      element.style.bottom = '20px';
      element.style.left = '20px';
      element.style.right = 'auto';
      element.style.top = 'auto';
    } else if (position === 'top-right') {
      element.style.top = '20px';
      element.style.right = '20px';
      element.style.left = 'auto';
      element.style.bottom = 'auto';
    }
  });

  // Control portal elements
  const portalElements = document.querySelectorAll('div[data-portal="true"]');
  portalElements.forEach(element => {
    const el = element as HTMLElement;
    el.style.position = 'fixed';
    el.style.zIndex = '999';
    el.style.pointerEvents = 'none';
    
    // Hide empty portal elements
    if (!el.children.length) {
      el.style.display = 'none';
    }
  });

  // Prevent horizontal overflow
  document.body.style.overflowX = 'hidden';
  const rootElement = document.getElementById('root');
  if (rootElement) {
    rootElement.style.overflowX = 'hidden';
    rootElement.style.position = 'relative';
  }
}

// Run cleanup on DOM content loaded
if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', cleanupProblematicElements);
  } else {
    cleanupProblematicElements();
  }
}

// Run cleanup periodically to catch dynamically added elements
if (typeof window !== 'undefined') {
  setInterval(cleanupProblematicElements, 2000);
}

// Export for manual use
export default cleanupProblematicElements;
