import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import authAPI from '../api/authAPI';

const AUTH_TOKEN_KEY = 'auth_token';
const AUTH_USER_KEY = 'auth_user';

const saveAuthData = (token, user) => {
  if (!token || !user) return;
  localStorage.setItem(AUTH_TOKEN_KEY, token);
  localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
};

const clearAuthData = () => {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(AUTH_USER_KEY);
};

const initialState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  error: null
};

export const login = createAsyncThunk(
  'auth/login',
  async (credentials, { rejectWithValue }) => {
    try {
      const response = await authAPI.login(credentials);
      if (!response?.token || !response?.user) {
        throw new Error('Invalid response format');
      }
      saveAuthData(response.token, response.user);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: error.message });
    }
  }
);

export const register = createAsyncThunk(
  'auth/register',
  async (userData, { rejectWithValue }) => {
    try {
      const response = await authAPI.register(userData);
      if (!response?.token || !response?.user) {
        throw new Error('Invalid response format');
      }
      saveAuthData(response.token, response.user);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data || { message: error.message });
    }
  }
);

export const logout = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      await authAPI.logout();
      clearAuthData();
      return null;
    } catch (error) {
      clearAuthData();
      return rejectWithValue(error.response?.data || { message: error.message });
    }
  }
);

export const checkAuthStatus = createAsyncThunk(
  'auth/checkStatus',
  async (_, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem(AUTH_TOKEN_KEY);
      if (!token) throw new Error('No token found');
      
      const response = await authAPI.validateToken(token);
      if (!response?.user) throw new Error('Invalid user data');
      
      return { user: response.user, token };
    } catch (error) {
      clearAuthData();
      return rejectWithValue(error.response?.data || { message: error.message });
    }
  }
);

const loadInitialState = () => {
  try {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    const userStr = localStorage.getItem(AUTH_USER_KEY);
    const user = userStr ? JSON.parse(userStr) : null;
    
    if (!token || !user) {
      clearAuthData();
      return initialState;
    }
    
    return {
      ...initialState,
      user,
      token,
      isAuthenticated: true
    };
  } catch {
    clearAuthData();
    return initialState;
  }
};

const authSlice = createSlice({
  name: 'auth',
  initialState: loadInitialState(),
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    updateUserPreferences: (state, action) => {
      if (state.user && action.payload) {
        state.user.preferences = {
          ...state.user.preferences,
          ...action.payload
        };
        localStorage.setItem(AUTH_USER_KEY, JSON.stringify(state.user));
      }
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.error = null;
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload?.message || 'Authentication failed';
        state.isAuthenticated = false;
      })
      .addCase(register.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.error = null;
      })
      .addCase(register.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload?.message || 'Registration failed';
        state.isAuthenticated = false;
      })
      .addCase(logout.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(logout.fulfilled, (state) => {
        Object.assign(state, initialState);
      })
      .addCase(logout.rejected, (state) => {
        Object.assign(state, initialState);
      })
      .addCase(checkAuthStatus.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(checkAuthStatus.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.error = null;
      })
      .addCase(checkAuthStatus.rejected, (state) => {
        Object.assign(state, initialState);
      });
  }
});

export const { clearError, updateUserPreferences } = authSlice.actions;
export default authSlice.reducer;