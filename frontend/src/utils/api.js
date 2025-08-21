import axios from 'axios';
import toast from 'react-hot-toast';

const BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API_VERSION = process.env.REACT_APP_API_VERSION || 'api';

// Create axios instance
const api = axios.create({
  baseURL: `${BASE_URL}/${API_VERSION}`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add timestamp to prevent caching
    config.params = {
      ...config.params,
      _t: Date.now(),
    };

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 errors (unauthorized)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Try to refresh token
        const { useAuthStore } = await import('../stores/useAuthStore');
        const refreshToken = useAuthStore.getState().refreshToken;

        if (refreshToken) {
          await useAuthStore.getState().refreshAccessToken();
          // Retry original request
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        const { useAuthStore } = await import('../stores/useAuthStore');
        useAuthStore.getState().logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    // Handle 403 errors (forbidden)
    if (error.response?.status === 403) {
      toast.error('You do not have permission to perform this action');
    }

    // Handle 404 errors
    if (error.response?.status === 404) {
      toast.error('The requested resource was not found');
    }

    // Handle 429 errors (rate limiting)
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after'];
      toast.error(`Too many requests. Please try again in ${retryAfter || 60} seconds`);
    }

    // Handle 500 errors (server errors)
    if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later');
    }

    // Handle network errors
    if (!error.response) {
      toast.error('Network error. Please check your connection');
    }

    return Promise.reject(error);
  }
);

export default api;

// Utility functions for common API patterns

export const apiClient = {
  // GET request with error handling
  get: async (url, config = {}) => {
    try {
      const response = await api.get(url, config);
      return { data: response.data, success: true };
    } catch (error) {
      return { 
        data: null, 
        success: false, 
        error: error.response?.data?.detail || error.message 
      };
    }
  },

  // POST request with error handling
  post: async (url, data = {}, config = {}) => {
    try {
      const response = await api.post(url, data, config);
      return { data: response.data, success: true };
    } catch (error) {
      return { 
        data: null, 
        success: false, 
        error: error.response?.data?.detail || error.message 
      };
    }
  },

  // PUT request with error handling
  put: async (url, data = {}, config = {}) => {
    try {
      const response = await api.put(url, data, config);
      return { data: response.data, success: true };
    } catch (error) {
      return { 
        data: null, 
        success: false, 
        error: error.response?.data?.detail || error.message 
      };
    }
  },

  // DELETE request with error handling
  delete: async (url, config = {}) => {
    try {
      const response = await api.delete(url, config);
      return { data: response.data, success: true };
    } catch (error) {
      return { 
        data: null, 
        success: false, 
        error: error.response?.data?.detail || error.message 
      };
    }
  },
};

// Upload file utility
export const uploadFile = async (url, file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await api.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    });

    return { data: response.data, success: true };
  } catch (error) {
    return { 
      data: null, 
      success: false, 
      error: error.response?.data?.detail || error.message 
    };
  }
};

// Download file utility
export const downloadFile = async (url, filename) => {
  try {
    const response = await api.get(url, {
      responseType: 'blob',
    });

    // Create blob link to download
    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(downloadUrl);

    return { success: true };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || error.message 
    };
  }
};