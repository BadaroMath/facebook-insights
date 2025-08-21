// Application constants

export const APP_CONFIG = {
  name: process.env.REACT_APP_APP_NAME || 'Facebook Analytics Platform',
  version: process.env.REACT_APP_APP_VERSION || '1.0.0',
  environment: process.env.REACT_APP_ENVIRONMENT || 'development',
};

export const API_CONFIG = {
  baseUrl: process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001',
  version: process.env.REACT_APP_API_VERSION || 'api',
  timeout: 30000,
};

export const FACEBOOK_CONFIG = {
  appId: process.env.REACT_APP_FACEBOOK_APP_ID,
  permissions: [
    'pages_show_list',
    'pages_read_engagement',
    'pages_read_user_content',
    'read_insights',
  ],
};

export const FEATURE_FLAGS = {
  darkMode: process.env.REACT_APP_ENABLE_DARK_MODE === 'true',
  notifications: process.env.REACT_APP_ENABLE_NOTIFICATIONS === 'true',
  export: process.env.REACT_APP_ENABLE_EXPORT === 'true',
};

export const CHART_CONFIG = {
  theme: process.env.REACT_APP_DEFAULT_CHART_THEME || 'light',
  animationDuration: parseInt(process.env.REACT_APP_ANIMATION_DURATION) || 300,
  colors: {
    primary: '#3b82f6',
    secondary: '#6b7280',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
    info: '#06b6d4',
  },
};

export const DATE_FORMATS = {
  display: 'MMM dd, yyyy',
  input: 'yyyy-MM-dd',
  api: 'yyyy-MM-dd',
  timestamp: 'yyyy-MM-dd HH:mm:ss',
};

export const PAGINATION = {
  defaultPageSize: 25,
  pageSizeOptions: [10, 25, 50, 100],
  maxPages: 10,
};

export const VALIDATION = {
  email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  password: {
    minLength: 8,
    requireUppercase: true,
    requireLowercase: true,
    requireNumbers: true,
    requireSpecialChars: false,
  },
};

export const ROUTES = {
  home: '/',
  login: '/login',
  register: '/register',
  dashboard: '/dashboard',
  analytics: '/analytics',
  pages: '/pages',
  posts: '/posts',
  reports: '/reports',
  settings: '/settings',
};

export const STORAGE_KEYS = {
  authToken: 'auth-token',
  refreshToken: 'refresh-token',
  user: 'user-data',
  theme: 'app-theme',
  language: 'app-language',
  preferences: 'user-preferences',
};

export const POST_TYPES = {
  PHOTO: 'photo',
  VIDEO: 'video',
  LINK: 'link',
  STATUS: 'status',
  EVENT: 'event',
  OFFER: 'offer',
};

export const REPORT_TYPES = {
  PAGE_PERFORMANCE: 'page_performance',
  POST_ANALYSIS: 'post_analysis',
  ENGAGEMENT_SUMMARY: 'engagement_summary',
  GROWTH_REPORT: 'growth_report',
  COMPETITIVE_ANALYSIS: 'competitive_analysis',
  CUSTOM: 'custom',
};

export const REPORT_FORMATS = {
  PDF: 'pdf',
  CSV: 'csv',
  EXCEL: 'excel',
  JSON: 'json',
};

export const REPORT_STATUS = {
  PENDING: 'pending',
  GENERATING: 'generating',
  COMPLETED: 'completed',
  FAILED: 'failed',
  EXPIRED: 'expired',
};

export const METRIC_TYPES = {
  PAGE_DAILY: 'page_daily',
  PAGE_LIFETIME: 'page_lifetime',
  POST_LIFETIME: 'post_lifetime',
  VIDEO_METRICS: 'video_metrics',
};

export const NOTIFICATION_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info',
};

export const SOCIAL_SHARE_URLS = {
  facebook: (url, text) => 
    `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
  twitter: (url, text) => 
    `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`,
  linkedin: (url, text) => 
    `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`,
  email: (url, text) => 
    `mailto:?subject=${encodeURIComponent(text)}&body=${encodeURIComponent(url)}`,
};

export const ANALYTICS_PERIODS = {
  LAST_7_DAYS: 7,
  LAST_30_DAYS: 30,
  LAST_90_DAYS: 90,
  LAST_YEAR: 365,
  CUSTOM: 'custom',
};

export const CHART_TYPES = {
  LINE: 'line',
  BAR: 'bar',
  PIE: 'pie',
  DOUGHNUT: 'doughnut',
  AREA: 'area',
  SCATTER: 'scatter',
};

export const FILE_TYPES = {
  IMAGE: ['jpg', 'jpeg', 'png', 'gif', 'webp'],
  VIDEO: ['mp4', 'avi', 'mov', 'wmv', 'flv'],
  DOCUMENT: ['pdf', 'doc', 'docx', 'txt', 'rtf'],
  SPREADSHEET: ['xls', 'xlsx', 'csv'],
  ARCHIVE: ['zip', 'rar', '7z', 'tar', 'gz'],
};

export const MAX_FILE_SIZE = {
  IMAGE: 5 * 1024 * 1024, // 5MB
  VIDEO: 100 * 1024 * 1024, // 100MB
  DOCUMENT: 10 * 1024 * 1024, // 10MB
  DEFAULT: 5 * 1024 * 1024, // 5MB
};

export const BREAKPOINTS = {
  xs: '480px',
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
};

export const ANIMATION_DURATIONS = {
  fast: 150,
  normal: 300,
  slow: 500,
  slower: 1000,
};

export const Z_INDEX = {
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modal: 1040,
  popover: 1050,
  tooltip: 1060,
  toast: 1070,
};