import axios from 'axios';
import type { AxiosResponse } from 'axios';

// ADD INTERFACE IMPORTS HERE:
import type {
  AnalysisResult,
  HealthCheckResponse,
  TextStatistics,
  AIPatterns,
  KeywordAnalysis,
  SuspiciousSection,
  ComprehensiveAnalysisResult
} from '../types/api';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds for file uploads
});

// Request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.data);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

export const analyzeResume = async (file: File): Promise<AnalysisResult> => {
  const formData = new FormData();
  formData.append('file', file);

  const response: AxiosResponse<AnalysisResult> = await api.post('/analyze/resume', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const healthCheck = async (): Promise<HealthCheckResponse> => {
  const response: AxiosResponse<HealthCheckResponse> = await api.get('/health');
  return response.data;
};

export const checkAIHealth = async (): Promise<any> => {
  const response: AxiosResponse<any> = await api.get('/health/ai');
  return response.data;
};

export default api;
