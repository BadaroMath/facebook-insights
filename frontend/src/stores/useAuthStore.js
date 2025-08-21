import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from '../utils/api';
import toast from 'react-hot-toast';

const useAuthStore = create(
  persist(
    (set, get) => ({
      // State
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,

      // Actions
      login: async (email, password) => {
        try {
          set({ isLoading: true });
          
          const response = await api.post('/auth/login', {
            email,
            password,
          });

          const { access_token, refresh_token, user } = response.data;

          set({
            user,
            accessToken: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false,
          });

          // Set token in API client
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

          toast.success('Successfully logged in!');
          return { success: true };
          
        } catch (error) {
          set({ isLoading: false });
          const message = error.response?.data?.detail || 'Login failed';
          toast.error(message);
          return { success: false, error: message };
        }
      },

      register: async (email, password, fullName) => {
        try {
          set({ isLoading: true });
          
          const response = await api.post('/auth/register', {
            email,
            password,
            full_name: fullName,
          });

          const { access_token, refresh_token, user } = response.data;

          set({
            user,
            accessToken: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false,
          });

          // Set token in API client
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

          toast.success('Account created successfully!');
          return { success: true };
          
        } catch (error) {
          set({ isLoading: false });
          const message = error.response?.data?.detail || 'Registration failed';
          toast.error(message);
          return { success: false, error: message };
        }
      },

      loginWithFacebook: async (accessToken) => {
        try {
          set({ isLoading: true });
          
          const response = await api.post('/auth/facebook', {
            access_token: accessToken,
          });

          const { access_token, refresh_token, user } = response.data;

          set({
            user,
            accessToken: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false,
          });

          // Set token in API client
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

          toast.success('Successfully logged in with Facebook!');
          return { success: true };
          
        } catch (error) {
          set({ isLoading: false });
          const message = error.response?.data?.detail || 'Facebook login failed';
          toast.error(message);
          return { success: false, error: message };
        }
      },

      logout: async () => {
        try {
          // Call logout endpoint
          await api.post('/auth/logout');
        } catch (error) {
          // Continue with logout even if API call fails
          console.error('Logout API call failed:', error);
        }

        // Clear state
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false,
        });

        // Clear API token
        delete api.defaults.headers.common['Authorization'];

        toast.success('Successfully logged out');
      },

      refreshAccessToken: async () => {
        try {
          const { refreshToken } = get();
          
          if (!refreshToken) {
            throw new Error('No refresh token available');
          }

          const response = await api.post('/auth/refresh', {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token: newRefreshToken, user } = response.data;

          set({
            user,
            accessToken: access_token,
            refreshToken: newRefreshToken,
            isAuthenticated: true,
          });

          // Update API token
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

          return access_token;
          
        } catch (error) {
          // If refresh fails, logout user
          get().logout();
          throw error;
        }
      },

      updateProfile: async (profileData) => {
        try {
          const response = await api.put('/users/profile', profileData);
          
          set({
            user: response.data,
          });

          toast.success('Profile updated successfully!');
          return { success: true };
          
        } catch (error) {
          const message = error.response?.data?.detail || 'Profile update failed';
          toast.error(message);
          return { success: false, error: message };
        }
      },

      // Initialize auth state
      initialize: () => {
        const { accessToken } = get();
        
        if (accessToken) {
          // Set token in API client
          api.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
          set({ isAuthenticated: true });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Initialize auth on app start
useAuthStore.getState().initialize();

export { useAuthStore };