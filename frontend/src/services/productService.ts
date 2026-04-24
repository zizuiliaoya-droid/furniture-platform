import api from './api';

export const productService = {
  getProducts: (params?: any) => api.get('/api/products/', { params }),
  getProduct: (id: number) => api.get(`/api/products/${id}/`),
  createProduct: (data: any) => api.post('/api/products/', data),
  updateProduct: (id: number, data: any) => api.patch(`/api/products/${id}/`, data),
  deleteProduct: (id: number) => api.delete(`/api/products/${id}/`),
  uploadImages: (id: number, formData: FormData) =>
    api.post(`/api/products/${id}/upload_images/`, formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  deleteImage: (imageId: number) => api.delete(`/api/products/images/${imageId}/`),
  setCoverImage: (imageId: number) => api.put(`/api/products/images/${imageId}/cover/`),
  updateImageOrder: (id: number, order: number[]) => api.put(`/api/products/${id}/images/order/`, { order }),
  importProducts: (formData: FormData, confirm?: boolean) =>
    api.post(`/api/products/import/${confirm ? '?confirm=true' : ''}`, formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  downloadTemplate: () => api.get('/api/products/import/template/', { responseType: 'blob' }),
  getConfigs: (productId: number) => api.get(`/api/products/${productId}/configs/`),
  createConfig: (productId: number, data: any) => api.post(`/api/products/${productId}/configs/`, data),
  updateConfig: (configId: number, data: any) => api.put(`/api/products/configs/${configId}/`, data),
  deleteConfig: (configId: number) => api.delete(`/api/products/configs/${configId}/`),
  getCategories: (params?: any) => api.get('/api/categories/', { params }),
  getCategoryTree: (dimension: string) => api.get('/api/categories/tree/', { params: { dimension } }),
  createCategory: (data: any) => api.post('/api/categories/', data),
  updateCategory: (id: number, data: any) => api.patch(`/api/categories/${id}/`, data),
  deleteCategory: (id: number) => api.delete(`/api/categories/${id}/`),
  reorderCategories: (items: any[]) => api.put('/api/categories/reorder/', { items }),
};
