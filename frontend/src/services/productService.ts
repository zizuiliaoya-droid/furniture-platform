import api from './api';

export const productService = {
  // ─── 产品 CRUD ─────────────────────────────────────────────────────────────
  getProducts: (params?: any) => api.get('/api/products/', { params }),
  getProduct: (id: number) => api.get(`/api/products/${id}/`),
  createProduct: (data: any) => api.post('/api/products/', data),
  createComposite: (payload: any, images: File[] = []) => {
    const formData = new FormData();
    formData.append('payload', JSON.stringify(payload));
    images.forEach((image) => formData.append('images', image));
    return api.post('/api/products/create-composite/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  updateProduct: (id: number, data: any) => api.patch(`/api/products/${id}/`, data),
  deleteProduct: (id: number, hard = false) => api.delete(`/api/products/${id}/${hard ? '?hard=true' : ''}`),
  reactivateProduct: (id: number) => api.post(`/api/products/${id}/reactivate/`),

  // ─── 图片管理 ──────────────────────────────────────────────────────────────
  uploadImages: (id: number, formData: FormData) =>
    api.post(`/api/products/${id}/upload_images/`, formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  deleteImage: (imageId: number) => api.delete(`/api/products/images/${imageId}/`),
  setCoverImage: (imageId: number) => api.put(`/api/products/images/${imageId}/cover/`),
  updateImageOrder: (id: number, order: number[]) => api.put(`/api/products/${id}/images/order/`, { order }),

  // ─── 产品批量导入（旧） ────────────────────────────────────────────────────
  importProducts: (formData: FormData, confirm?: boolean) =>
    api.post(`/api/products/import/${confirm ? '?confirm=true' : ''}`, formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  downloadImportTemplate: () => api.get('/api/products/import/template/', { responseType: 'blob' }),

  // ─── 批量产品导入（长格式，多产品） ────────────────────────────────────────
  batchImport: (file: File, confirm = false) => {
    const fd = new FormData();
    fd.append('file', file);
    return api.post(`/api/products/batch-import/${confirm ? '?confirm=true' : ''}`, fd,
      { headers: { 'Content-Type': 'multipart/form-data' } });
  },
  downloadBatchTemplate: () => api.get('/api/products/batch-template/', { responseType: 'blob' }),
  exportConfig: (id: number) => api.get(`/api/products/${id}/export-config/`, { responseType: 'blob' }),

  // ─── 旧配置（兼容保留） ────────────────────────────────────────────────────
  getConfigs: (productId: number) => api.get(`/api/products/${productId}/configs/`),
  createConfig: (productId: number, data: any) => api.post(`/api/products/${productId}/configs/`, data),
  updateConfig: (configId: number, data: any) => api.put(`/api/products/configs/${configId}/`, data),
  deleteConfig: (configId: number) => api.delete(`/api/products/configs/${configId}/`),

  // ─── 配置维度（新） ────────────────────────────────────────────────────────
  getConfigDimensions: (productId: number) =>
    api.get(`/api/products/${productId}/config-dimensions/`),
  addConfigDimension: (productId: number, data: any) =>
    api.post(`/api/products/${productId}/config-dimensions/add/`, data),

  // ─── 价格计算（新） ────────────────────────────────────────────────────────
  calculatePrice: (productId: number, selections: Record<string, string>) =>
    api.post(`/api/products/${productId}/calculate-price/`, { selections }),

  // ─── 配置 Excel 导入（新） ─────────────────────────────────────────────────
  uploadConfigExcel: (productId: number, file: File, confirm = false) => {
    const fd = new FormData();
    fd.append('file', file);
    return api.post(
      `/api/products/${productId}/upload-config-excel/${confirm ? '?confirm=true' : ''}`,
      fd,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
  },
  downloadConfigTemplate: () => api.get('/api/products/config-template/', { responseType: 'blob' }),

  // ─── 产品-文档关联（新） ───────────────────────────────────────────────────
  getProductDocuments: (productId: number, params?: any) =>
    api.get(`/api/products/${productId}/documents/`, { params }),
  linkDocument: (productId: number, payload: { document_id: number; relation_type: string }) =>
    api.post(`/api/products/${productId}/documents/`, payload),
  unlinkDocument: (productId: number, docId: number) =>
    api.delete(`/api/products/${productId}/documents/${docId}/`),

  // ─── 类别选项（新） ────────────────────────────────────────────────────────
  getCategoryOptions: () => api.get('/api/products/category-options/'),

  // ─── 分类（过渡保留） ──────────────────────────────────────────────────────
  getCategories: (params?: any) => api.get('/api/categories/', { params }),
  getCategoryTree: (dimension: string) => api.get('/api/categories/tree/', { params: { dimension } }),
  createCategory: (data: any) => api.post('/api/categories/', data),
  updateCategory: (id: number, data: any) => api.patch(`/api/categories/${id}/`, data),
  deleteCategory: (id: number) => api.delete(`/api/categories/${id}/`),
  reorderCategories: (items: any[]) => api.put('/api/categories/reorder/', { items }),
};
