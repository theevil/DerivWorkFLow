import type {
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  User,
  TradePosition,
  TradingStats,
  TradingParametersRequest,
} from '../types/trading';
import { config } from '../config/env';

const API_URL = config.apiUrl;

class ApiClient {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
  }

  clearToken() {
    this.token = null;
  }

  private async fetch<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    // Create abort controller for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), config.apiTimeout);

    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers: {
          ...headers,
          ...options.headers,
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('Request timeout');
        }
        throw error;
      }
      
      throw new Error('An unexpected error occurred');
    }
  }

  async login(data: LoginRequest): Promise<AuthResponse> {
    const formData = new URLSearchParams();
    formData.append('username', data.email);
    formData.append('password', data.password);

    const response = await fetch(`${API_URL}/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Login failed');
    }

    return response.json();
  }

  async register(data: RegisterRequest): Promise<User> {
    return this.fetch<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getCurrentUser(): Promise<User> {
    return this.fetch<User>('/auth/me');
  }

  // Trading endpoints
  async getPositions(status?: string): Promise<TradePosition[]> {
    const params = status ? `?status=${status}` : '';
    return this.fetch<TradePosition[]>(`/trading/positions${params}`);
  }

  async getTradingStats(): Promise<TradingStats> {
    return this.fetch<TradingStats>('/trading/stats');
  }

  async getTradingParameters(): Promise<TradingParametersRequest | null> {
    return this.fetch<TradingParametersRequest | null>('/trading/parameters');
  }

  async updateTradingParameters(params: TradingParametersRequest): Promise<TradingParametersRequest> {
    return this.fetch<TradingParametersRequest>('/trading/parameters', {
      method: 'PUT',
      body: JSON.stringify(params),
    });
  }

  async createTradingParameters(params: TradingParametersRequest): Promise<TradingParametersRequest> {
    return this.fetch<TradingParametersRequest>('/trading/parameters', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async closePosition(positionId: string): Promise<{ message: string }> {
    return this.fetch<{ message: string }>(`/trading/positions/${positionId}/close`, {
      method: 'PUT',
    });
  }
}

export const api = new ApiClient();
