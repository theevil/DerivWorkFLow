import { useState, useCallback, useRef, useEffect } from 'react';
import { http, HttpError, RequestConfig } from '../lib/http-client';

// Types for our API hook
export interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: HttpError | null;
  success: boolean;
  retryCount: number;
  lastUpdated: Date | null;
}

export interface ApiOptions extends RequestConfig {
  autoRetry?: boolean;
  fallbackData?: any;
  onSuccess?: (data: any) => void;
  onError?: (error: HttpError) => void;
  onFinally?: () => void;
  cacheTime?: number; // milliseconds
  refetchOnWindowFocus?: boolean;
  refetchOnMount?: boolean;
}

export interface ApiActions<T> {
  execute: (config?: RequestConfig) => Promise<T | null>;
  retry: () => Promise<T | null>;
  reset: () => void;
  cancel: () => void;
  refetch: () => Promise<T | null>;
}

export interface UseApiReturn<T> extends ApiState<T>, ApiActions<T> {
  isStale: boolean;
  isError: boolean;
  isSuccess: boolean;
  isIdle: boolean;
}

// Cache for storing API responses
const apiCache = new Map<
  string,
  { data: any; timestamp: number; ttl: number }
>();

// Generate cache key
const generateCacheKey = (url: string, config?: RequestConfig): string => {
  const configStr = config ? JSON.stringify(config) : '';
  return `${url}_${configStr}`;
};

// Check if cache is valid
const isCacheValid = (key: string, cacheTime: number): boolean => {
  const cached = apiCache.get(key);
  if (!cached) return false;

  const now = Date.now();
  return now - cached.timestamp < cacheTime;
};

// Get cached data
const getCachedData = (key: string): any => {
  const cached = apiCache.get(key);
  return cached ? cached.data : null;
};

// Set cache data
const setCachedData = (key: string, data: any, ttl: number): void => {
  apiCache.set(key, {
    data,
    timestamp: Date.now(),
    ttl,
  });
};

// Clean expired cache entries
const cleanExpiredCache = (): void => {
  const now = Date.now();
  for (const [key, cached] of apiCache.entries()) {
    if (now - cached.timestamp > cached.ttl) {
      apiCache.delete(key);
    }
  }
};

// Run cache cleanup periodically
setInterval(cleanExpiredCache, 60000); // Every minute

export function useApi<T = any>(
  url: string,
  options: ApiOptions = {}
): UseApiReturn<T> {
  const {
    autoRetry = true,
    fallbackData = null,
    onSuccess,
    onError,
    onFinally,
    cacheTime = 300000, // 5 minutes default
    refetchOnWindowFocus = false,
    refetchOnMount = true,
    ...requestConfig
  } = options;

  // State
  const [state, setState] = useState<ApiState<T>>({
    data: fallbackData,
    loading: false,
    error: null,
    success: false,
    retryCount: 0,
    lastUpdated: null,
  });

  // Refs
  const abortControllerRef = useRef<AbortController | null>(null);
  const cacheKeyRef = useRef<string>(generateCacheKey(url, requestConfig));
  const isMountedRef = useRef(true);

  // Update cache key when URL or config changes
  useEffect(() => {
    cacheKeyRef.current = generateCacheKey(url, requestConfig);
  }, [url, requestConfig]);

  // Check if data is stale
  const isStale = useCallback(() => {
    if (!state.lastUpdated) return true;
    const now = Date.now();
    return now - state.lastUpdated.getTime() > cacheTime;
  }, [state.lastUpdated, cacheTime]);

  // Execute API request
  const execute = useCallback(
    async (config?: RequestConfig): Promise<T | null> => {
      const finalConfig = { ...requestConfig, ...config };

      // Check cache first
      const cachedData = getCachedData(cacheKeyRef.current);
      if (cachedData && !isStale()) {
        setState(prev => ({
          ...prev,
          data: cachedData,
          success: true,
          loading: false,
          error: null,
        }));
        return cachedData;
      }

      // Cancel previous request if any
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      // Create new abort controller
      abortControllerRef.current = new AbortController();
      finalConfig.signal = abortControllerRef.current.signal;

      setState(prev => ({
        ...prev,
        loading: true,
        error: null,
        success: false,
      }));

      try {
        const response = await (http as any).get(url, config);

        if (!isMountedRef.current) return null;

        const data = response.data;

        // Cache the response
        setCachedData(cacheKeyRef.current, data, cacheTime);

        setState(prev => ({
          ...prev,
          data,
          loading: false,
          success: true,
          error: null,
          lastUpdated: new Date(),
          retryCount: 0,
        }));

        onSuccess?.(data);
        return data;
      } catch (error) {
        if (!isMountedRef.current) return null;

        const httpError = error as HttpError;

        setState(prev => ({
          ...prev,
          loading: false,
          success: false,
          error: httpError,
          retryCount: prev.retryCount + 1,
        }));

        onError?.(httpError);

        // Auto-retry logic
        if (autoRetry && httpError.retryCount < (finalConfig.retries || 3)) {
          const delay = Math.min(
            1000 * Math.pow(2, httpError.retryCount),
            10000
          );

          setTimeout(() => {
            if (isMountedRef.current) {
              execute(config);
            }
          }, delay);
        }

        return null;
      } finally {
        if (isMountedRef.current) {
          setState(prev => ({ ...prev, loading: false }));
          onFinally?.();
        }
      }
    },
    [
      url,
      requestConfig,
      autoRetry,
      cacheTime,
      onSuccess,
      onError,
      onFinally,
      isStale,
    ]
  );

  // Retry function
  const retry = useCallback(async (): Promise<T | null> => {
    return execute();
  }, [execute]);

  // Reset state
  const reset = useCallback(() => {
    setState({
      data: fallbackData,
      loading: false,
      error: null,
      success: false,
      retryCount: 0,
      lastUpdated: null,
    });
  }, [fallbackData]);

  // Cancel request
  const cancel = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setState(prev => ({ ...prev, loading: false }));
  }, []);

  // Refetch data
  const refetch = useCallback(async (): Promise<T | null> => {
    // Clear cache for this key
    apiCache.delete(cacheKeyRef.current);
    return execute();
  }, [execute]);

  // Auto-execute on mount if enabled
  useEffect(() => {
    if (refetchOnMount) {
      execute();
    }
  }, [execute, refetchOnMount]);

  // Auto-refetch on window focus if enabled
  useEffect(() => {
    if (!refetchOnWindowFocus) return;

    const handleFocus = () => {
      if (isStale()) {
        refetch();
      }
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [refetchOnWindowFocus, refetch, isStale]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  // Computed properties
  const isError = !!state.error;
  const isSuccess = state.success;
  const isIdle = !state.loading && !state.success && !state.error;

  return {
    ...state,
    execute,
    retry,
    reset,
    cancel,
    refetch,
    isStale: isStale(),
    isError,
    isSuccess,
    isIdle,
  };
}

// Specialized hooks for common HTTP methods
export function useGet<T = any>(
  url: string,
  options?: ApiOptions
): UseApiReturn<T> {
  return useApi<T>(url, { ...options, method: 'GET' });
}

export function usePost<T = any>(
  url: string,
  options?: ApiOptions
): UseApiReturn<T> {
  return useApi<T>(url, { ...options, method: 'POST' });
}

export function usePut<T = any>(
  url: string,
  options?: ApiOptions
): UseApiReturn<T> {
  return useApi<T>(url, { ...options, method: 'PUT' });
}

export function useDelete<T = any>(
  url: string,
  options?: ApiOptions
): UseApiReturn<T> {
  return useApi<T>(url, { ...options, method: 'DELETE' });
}

export function usePatch<T = any>(
  url: string,
  options?: ApiOptions
): UseApiReturn<T> {
  return useApi<T>(url, { ...options, method: 'PATCH' });
}

// Hook for API health monitoring
export function useApiHealth() {
  const [isHealthy, setIsHealthy] = useState(true);
  const [lastCheck, setLastCheck] = useState<Date | null>(null);

  const checkHealth = useCallback(async () => {
    try {
      const healthy = await http.healthCheck();
      setIsHealthy(healthy);
      setLastCheck(new Date());
      return healthy;
    } catch {
      setIsHealthy(false);
      setLastCheck(new Date());
      return false;
    }
  }, []);

  useEffect(() => {
    checkHealth();

    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  return {
    isHealthy,
    lastCheck,
    checkHealth,
  };
}

// Hook for API statistics
export function useApiStats() {
  const [stats, setStats] = useState(http.getStats());

  useEffect(() => {
    const updateStats = () => setStats(http.getStats());

    // Update stats every second
    const interval = setInterval(updateStats, 1000);
    return () => clearInterval(interval);
  }, []);

  return stats;
}
