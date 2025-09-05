import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { http } from '../../lib/http-client';
import {
  TradingPosition,
  MarketData,
  TradingOrder,
  TradingState,
  OpenPositionRequest,
  ClosePositionRequest,
  PlaceOrderRequest,
} from '../../models';

// Initial state
const initialState: TradingState = {
  positions: [],
  orders: [],
  marketData: {},
  portfolio: {
    balance: 0,
    equity: 0,
    margin: 0,
    freeMargin: 0,
    marginLevel: 0,
    totalPnL: 0,
    dailyPnL: 0,
  },
  isLoading: false,
  error: null,
  lastUpdate: null,
  selectedSymbol: null,
  tradingEnabled: false,
  riskLevel: 'medium',
};

// Async thunks
export const fetchPositions = createAsyncThunk(
  'trading/fetchPositions',
  async (_, { rejectWithValue }) => {
    try {
      const response = await http.get<TradingPosition[]>('/trading/positions');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch positions');
    }
  }
);

export const fetchOrders = createAsyncThunk(
  'trading/fetchOrders',
  async (_, { rejectWithValue }) => {
    try {
      const response = await http.get<TradingOrder[]>('/trading/orders');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch orders');
    }
  }
);

export const fetchMarketData = createAsyncThunk(
  'trading/fetchMarketData',
  async (symbols: string[], { rejectWithValue }) => {
    try {
      const response = await http.get<Record<string, MarketData>>(
        '/trading/market-data',
        {
          params: { symbols: symbols.join(',') },
        }
      );
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch market data');
    }
  }
);

export const fetchPortfolio = createAsyncThunk(
  'trading/fetchPortfolio',
  async (_, { rejectWithValue }) => {
    try {
      const response =
        await http.get<typeof initialState.portfolio>('/trading/portfolio');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch portfolio');
    }
  }
);

export const openPosition = createAsyncThunk(
  'trading/openPosition',
  async (request: OpenPositionRequest, { rejectWithValue }) => {
    try {
      const response = await http.post<TradingPosition>(
        '/trading/positions',
        request
      );
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to open position');
    }
  }
);

export const closePosition = createAsyncThunk(
  'trading/closePosition',
  async (request: ClosePositionRequest, { rejectWithValue }) => {
    try {
      const response = await http.post<TradingPosition>(
        '/trading/positions/close',
        request
      );
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to close position');
    }
  }
);

export const placeOrder = createAsyncThunk(
  'trading/placeOrder',
  async (request: PlaceOrderRequest, { rejectWithValue }) => {
    try {
      const response = await http.post<TradingOrder>(
        '/trading/orders',
        request
      );
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to place order');
    }
  }
);

export const cancelOrder = createAsyncThunk(
  'trading/cancelOrder',
  async (orderId: string, { rejectWithValue }) => {
    try {
      const response = await http.delete<TradingOrder>(
        `/trading/orders/${orderId}`
      );
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to cancel order');
    }
  }
);

// Trading slice
const tradingSlice = createSlice({
  name: 'trading',
  initialState,
  reducers: {
    // Clear error
    clearError: state => {
      state.error = null;
    },

    // Set selected symbol
    setSelectedSymbol: (state, action: PayloadAction<string>) => {
      state.selectedSymbol = action.payload;
    },

    // Set trading enabled
    setTradingEnabled: (state, action: PayloadAction<boolean>) => {
      state.tradingEnabled = action.payload;
    },

    // Set risk level
    setRiskLevel: (state, action: PayloadAction<'low' | 'medium' | 'high'>) => {
      state.riskLevel = action.payload;
    },

    // Update market data for a symbol
    updateMarketData: (
      state,
      action: PayloadAction<{ symbol: string; data: MarketData }>
    ) => {
      const { symbol, data } = action.payload;
      state.marketData[symbol] = data;
      state.lastUpdate = new Date().toISOString();
    },

    // Update position
    updatePosition: (state, action: PayloadAction<TradingPosition>) => {
      const index = state.positions.findIndex(p => p.id === action.payload.id);
      if (index !== -1) {
        state.positions[index] = action.payload;
      }
    },

    // Update order
    updateOrder: (state, action: PayloadAction<TradingOrder>) => {
      const index = state.orders.findIndex(o => o.id === action.payload.id);
      if (index !== -1) {
        state.orders[index] = action.payload;
      }
    },

    // Remove position
    removePosition: (state, action: PayloadAction<string>) => {
      state.positions = state.positions.filter(p => p.id !== action.payload);
    },

    // Remove order
    removeOrder: (state, action: PayloadAction<string>) => {
      state.orders = state.orders.filter(o => o.id !== action.payload);
    },

    // Set loading state
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },

    // Reset trading state
    resetTrading: state => {
      state.positions = [];
      state.orders = [];
      state.marketData = {};
      state.portfolio = initialState.portfolio;
      state.error = null;
      state.lastUpdate = null;
      state.selectedSymbol = null;
      state.tradingEnabled = false;
    },
  },
  extraReducers: builder => {
    // Fetch positions
    builder
      .addCase(fetchPositions.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchPositions.fulfilled, (state, action) => {
        state.isLoading = false;
        state.positions = action.payload;
        state.lastUpdate = new Date().toISOString();
      })
      .addCase(fetchPositions.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Fetch orders
    builder
      .addCase(fetchOrders.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchOrders.fulfilled, (state, action) => {
        state.isLoading = false;
        state.orders = action.payload;
        state.lastUpdate = new Date().toISOString();
      })
      .addCase(fetchOrders.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Fetch market data
    builder
      .addCase(fetchMarketData.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchMarketData.fulfilled, (state, action) => {
        state.isLoading = false;
        state.marketData = { ...state.marketData, ...action.payload };
        state.lastUpdate = new Date().toISOString();
      })
      .addCase(fetchMarketData.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Fetch portfolio
    builder
      .addCase(fetchPortfolio.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchPortfolio.fulfilled, (state, action) => {
        state.isLoading = false;
        state.portfolio = action.payload;
        state.lastUpdate = new Date().toISOString();
      })
      .addCase(fetchPortfolio.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Open position
    builder
      .addCase(openPosition.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(openPosition.fulfilled, (state, action) => {
        state.isLoading = false;
        state.positions.push(action.payload);
        state.lastUpdate = new Date().toISOString();
      })
      .addCase(openPosition.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Close position
    builder
      .addCase(closePosition.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(closePosition.fulfilled, (state, action) => {
        state.isLoading = false;
        const index = state.positions.findIndex(
          p => p.id === action.payload.id
        );
        if (index !== -1) {
          state.positions[index] = action.payload;
        }
        state.lastUpdate = new Date().toISOString();
      })
      .addCase(closePosition.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Place order
    builder
      .addCase(placeOrder.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(placeOrder.fulfilled, (state, action) => {
        state.isLoading = false;
        state.orders.push(action.payload);
        state.lastUpdate = new Date().toISOString();
      })
      .addCase(placeOrder.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Cancel order
    builder
      .addCase(cancelOrder.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(cancelOrder.fulfilled, (state, action) => {
        state.isLoading = false;
        const index = state.orders.findIndex(o => o.id === action.payload.id);
        if (index !== -1) {
          state.orders[index] = action.payload;
        }
        state.lastUpdate = new Date().toISOString();
      })
      .addCase(cancelOrder.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

// Export actions
export const {
  clearError,
  setSelectedSymbol,
  setTradingEnabled,
  setRiskLevel,
  updateMarketData,
  updatePosition,
  updateOrder,
  removePosition,
  removeOrder,
  setLoading,
  resetTrading,
} = tradingSlice.actions;

// Export selectors
export const selectTrading = (state: { trading: TradingState }) =>
  state.trading;
export const selectPositions = (state: { trading: TradingState }) =>
  state.trading.positions;
export const selectOrders = (state: { trading: TradingState }) =>
  state.trading.orders;
export const selectMarketData = (state: { trading: TradingState }) =>
  state.trading.marketData;
export const selectPortfolio = (state: { trading: TradingState }) =>
  state.trading.portfolio;
export const selectIsLoading = (state: { trading: TradingState }) =>
  state.trading.isLoading;
export const selectError = (state: { trading: TradingState }) =>
  state.trading.error;
export const selectSelectedSymbol = (state: { trading: TradingState }) =>
  state.trading.selectedSymbol;
export const selectTradingEnabled = (state: { trading: TradingState }) =>
  state.trading.tradingEnabled;
export const selectRiskLevel = (state: { trading: TradingState }) =>
  state.trading.riskLevel;

// Export reducer
export default tradingSlice.reducer;
