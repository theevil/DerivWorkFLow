import type {
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  User,
  TradePosition,
  TradingStats,
  TradingParametersRequest,
} from '../types/trading';
import type {
  SystemStatus,
  AutoTradingConfig,
  AutomationConfigResponse,
  EmergencyStopRequest,
  EmergencyStopResponse,
  TriggerTaskResponse,
  TaskStatus,
  ActiveTask,
  Alert,
  AutomationPerformance,
  HealthCheckResponse,
} from '../types/automation';
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

  async setDerivToken(token: string): Promise<{ message: string }> {
    return this.fetch<{ message: string }>('/deriv/token', {
      method: 'POST',
      body: JSON.stringify({ token }),
    });
  }

  async updateSettings(settings: any): Promise<{ message: string }> {
    return this.fetch<{ message: string }>('/settings/settings', {
      method: 'PUT',
      body: JSON.stringify(settings),
    });
  }

  async closePosition(positionId: string): Promise<{ message: string }> {
    return this.fetch<{ message: string }>(`/trading/positions/${positionId}/close`, {
      method: 'PUT',
    });
  }

  // Automation endpoints
  async getAutomationStatus(): Promise<SystemStatus> {
    return this.fetch<SystemStatus>('/automation/status');
  }

  async getAutoTradingConfig(): Promise<AutomationConfigResponse> {
    return this.fetch<AutomationConfigResponse>('/automation/auto-trading/config');
  }

  async configureAutoTrading(config: AutoTradingConfig): Promise<{ message: string; config: AutoTradingConfig; user_id: string }> {
    return this.fetch<{ message: string; config: AutoTradingConfig; user_id: string }>('/automation/auto-trading/configure', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  }

  async triggerEmergencyStop(request: EmergencyStopRequest): Promise<EmergencyStopResponse> {
    return this.fetch<EmergencyStopResponse>('/automation/emergency-stop', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async triggerMarketScan(): Promise<TriggerTaskResponse> {
    return this.fetch<TriggerTaskResponse>('/automation/market-scan/trigger', {
      method: 'POST',
    });
  }

  async triggerPositionMonitor(): Promise<TriggerTaskResponse> {
    return this.fetch<TriggerTaskResponse>('/automation/position-monitor/trigger', {
      method: 'POST',
    });
  }

  async triggerModelRetrain(): Promise<TriggerTaskResponse> {
    return this.fetch<TriggerTaskResponse>('/automation/models/retrain', {
      method: 'POST',
    });
  }

  async getTaskStatus(taskId: string): Promise<TaskStatus> {
    return this.fetch<TaskStatus>(`/automation/tasks/${taskId}/status`);
  }

  async getActiveTasks(): Promise<{ active_tasks: Record<string, ActiveTask[]>; scheduled_tasks: Record<string, ActiveTask[]>; timestamp: string }> {
    return this.fetch<{ active_tasks: Record<string, ActiveTask[]>; scheduled_tasks: Record<string, ActiveTask[]>; timestamp: string }>('/automation/tasks/active');
  }

  async getQueueStats(): Promise<{ queue_lengths: Record<string, { length: number; queue_key: string }>; worker_stats: any; timestamp: string }> {
    return this.fetch<{ queue_lengths: Record<string, { length: number; queue_key: string }>; worker_stats: any; timestamp: string }>('/automation/queue-stats');
  }

  async runHealthCheck(): Promise<HealthCheckResponse> {
    return this.fetch<HealthCheckResponse>('/automation/health-check', {
      method: 'POST',
    });
  }

  async getUserAlerts(): Promise<{ alerts: Alert[]; total_count: number; unacknowledged_count: number }> {
    return this.fetch<{ alerts: Alert[]; total_count: number; unacknowledged_count: number }>('/automation/alerts');
  }

  async acknowledgeAlert(alertId: string): Promise<{ message: string; alert_id: string }> {
    return this.fetch<{ message: string; alert_id: string }>(`/automation/alerts/${alertId}/acknowledge`, {
      method: 'POST',
    });
  }

  async getAutomationPerformance(days: number = 7): Promise<AutomationPerformance> {
    return this.fetch<AutomationPerformance>(`/automation/performance/summary?days=${days}`);
  }
}

export const api = new ApiClient();
