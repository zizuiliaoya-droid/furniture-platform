import api from './api';

export const shareService = {
  getShares: () => api.get('/api/shares/'),
  createShare: (data: any) => api.post('/api/shares/', data),
  deleteShare: (id: number) => api.delete(`/api/shares/${id}/`),
  getSharedContent: (token: string) => api.get(`/api/share/${token}/`),
  verifyPassword: (token: string, password: string) => api.post(`/api/share/${token}/verify/`, { password }),
  trackClick: (token: string, data: any) => api.post(`/api/share/${token}/track/`, data),
};
