import api from './api';

export const caseService = {
  getCases: (params?: any) => api.get('/api/cases/', { params }),
  getCase: (id: number) => api.get(`/api/cases/${id}/`),
  createCase: (data: any) => api.post('/api/cases/', data),
  updateCase: (id: number, data: any) => api.patch(`/api/cases/${id}/`, data),
  deleteCase: (id: number) => api.delete(`/api/cases/${id}/`),
  uploadImages: (id: number, formData: FormData) =>
    api.post(`/api/cases/${id}/upload_images/`, formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  deleteImage: (imageId: number) => api.delete(`/api/cases/images/${imageId}/`),
};
