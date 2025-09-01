import type {
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  UserResponse,
  TradePosition,
  TradingStats,
  TradingParametersRequest,
} from '@deriv-workflow/shared';

const API_URL = 'http://localhost:8000/api/v1';

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

    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers: {
        ...headers,
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'An error occurred');
    }

    return response.json();
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

  async register(data: RegisterRequest): Promise<UserResponse> {
    return this.fetch<UserResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getCurrentUser(): Promise<UserResponse> {
    return this.fetch<UserResponse>('/auth/me');
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
