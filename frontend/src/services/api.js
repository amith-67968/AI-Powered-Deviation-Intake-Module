import axios from 'axios';

const api = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api', timeout: 60000 });

export const analyzeDeviation = (text, file) => {
  const data = new FormData();
  if (text?.trim()) data.append('text', text.trim());
  if (file) data.append('file', file);
  return api.post('/deviations/analyze', data);
};
export const saveDeviation = (payload) => api.post('/deviations', payload);
export const getDeviations = (q) => api.get('/deviations', { params: q ? { q } : {} });
export const getDeviation = (id) => api.get(`/deviations/${id}`);
export const updateDeviation = (id, payload) => api.put(`/deviations/${id}`, payload);
export const askDeviationAssistant = (question, deviation_context) => api.post('/deviations/chat', { question, deviation_context });

export const apiError = (error, fallback = 'Something went wrong. Please try again.') => error?.response?.data?.detail || fallback;
