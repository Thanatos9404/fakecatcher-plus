import axios from 'axios';
import type { AxiosResponse } from 'axios';

// ✅ Import the correct types
import type {
  JobAnalysisResult,
  ComprehensiveAnalysisResult,
  HealthCheckResponse
} from '../types/api';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Request and response interceptors remain the same...
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

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

// ✅ Updated resume analysis function using ComprehensiveAnalysisResult
export const analyzeResume = async (file: File): Promise<ComprehensiveAnalysisResult> => {
  const formData = new FormData();
  formData.append('file', file);

  const response: AxiosResponse<ComprehensiveAnalysisResult> = await api.post('/analyze/resume', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

// Job posting analysis functions remain the same...
export const analyzeJobPosting = async (params: {
  file?: File;
  url?: string;
  type?: 'image' | 'pdf';
}): Promise<JobAnalysisResult> => {
  if (params.file) {
    const formData = new FormData();
    formData.append('file', params.file);

    const response: AxiosResponse<JobAnalysisResult> = await api.post('/analyze/job/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } else if (params.url) {
    const formData = new FormData();
    formData.append('job_url', params.url);

    const response: AxiosResponse<JobAnalysisResult> = await api.post('/analyze/job/url', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    return response.data;
  } else {
    throw new Error('Either file or URL must be provided for job posting analysis');
  }
};

// Health check functions...
export const healthCheck = async (): Promise<HealthCheckResponse> => {
  const response: AxiosResponse<HealthCheckResponse> = await api.get('/health');
  return response.data;
};

export const checkAIHealth = async (): Promise<HealthCheckResponse> => {
  const response: AxiosResponse<HealthCheckResponse> = await api.get('/health/ai');
  return response.data;
};

export const checkJobAnalyzerHealth = async (): Promise<HealthCheckResponse> => {
  const response: AxiosResponse<HealthCheckResponse> = await api.get('/health/job');
  return response.data;
};

export default api;
