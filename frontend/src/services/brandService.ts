import api from './api';

export const brandService = {
  getBrands: (params?: any) => api.get('/api/brands/', { params }),
  createBrand: (data: any) => api.post('/api/brands/', data),
  updateBrand: (id: number, data: any) => api.patch(`/api/brands/${id}/`, data),
  deleteBrand: (id: number) => api.delete(`/api/brands/${id}/`),
};
