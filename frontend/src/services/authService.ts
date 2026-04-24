import api from './api';

export const authService = {
  login: (username: string, password: string) =>
    api.post('/api/auth/login/', { username, password }),
  logout: () => api.post('/api/auth/logout/'),
  getMe: () => api.get('/api/auth/me/'),
  getUsers: (params?: any) => api.get('/api/auth/users/', { params }),
  createUser: (data: any) => api.post('/api/auth/users/', data),
  updateUser: (id: number, data: any) => api.put(`/api/auth/users/${id}/`, data),
  toggleUserStatus: (id: number) => api.post(`/api/auth/users/${id}/toggle-status/`),
  resetPassword: (id: number, newPassword: string) =>
    api.post(`/api/auth/users/${id}/reset-password/`, { new_password: newPassword }),
};
