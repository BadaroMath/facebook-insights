import { create } from 'zustand';
import api from '../utils/api';
import toast from 'react-hot-toast';

const useDashboardStore = create((set, get) => ({
  // State
  dashboardData: null,
  selectedPage: null,
  dateRange: {
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // 30 days ago
    end: new Date(),
  },
  isLoading: false,
  error: null,

  // Actions
  setSelectedPage: (page) => {
    set({ selectedPage: page });
    // Refresh dashboard data when page changes
    if (page) {
      get().fetchDashboardData(page.page_id);
    }
  },

  setDateRange: (start, end) => {
    set({ dateRange: { start, end } });
    // Refresh data with new date range
    const { selectedPage } = get();
    if (selectedPage) {
      get().fetchDashboardData(selectedPage.page_id);
    }
  },

  fetchDashboardData: async (pageId) => {
    try {
      set({ isLoading: true, error: null });

      const { dateRange } = get();
      const days = Math.ceil((dateRange.end - dateRange.start) / (1000 * 60 * 60 * 24));

      const response = await api.get(`/analytics/dashboard/${pageId}`, {
        params: { days },
      });

      set({
        dashboardData: response.data,
        isLoading: false,
      });

    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to fetch dashboard data';
      set({
        error: message,
        isLoading: false,
      });
      toast.error(message);
    }
  },

  clearDashboard: () => {
    set({
      dashboardData: null,
      selectedPage: null,
      error: null,
    });
  },
}));

export { useDashboardStore };