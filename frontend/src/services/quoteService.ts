import api from './api';

export interface AddItemFromProductPayload {
  product_id: number;
  selections: Record<string, string>;
  image_id?: number | null;
  quantity?: number;
  discount?: number;
}

export const quoteService = {
  getQuotes: (params?: any) => api.get('/api/quotes/', { params }),
  getQuote: (id: number) => api.get(`/api/quotes/${id}/`),
  createQuote: (data: any) => api.post('/api/quotes/', data),
  updateQuote: (id: number, data: any) => api.patch(`/api/quotes/${id}/`, data),
  deleteQuote: (id: number) => api.delete(`/api/quotes/${id}/`),
  duplicateQuote: (id: number) => api.post(`/api/quotes/${id}/duplicate/`),
  exportPdf: (id: number) => api.get(`/api/quotes/${id}/pdf/`, { responseType: 'blob' }),
  getItems: (quoteId: number) => api.get(`/api/quotes/${quoteId}/items/`),
  addItem: (quoteId: number, data: any) => api.post(`/api/quotes/${quoteId}/items/`, data),
  updateItem: (itemId: number, data: any) => api.patch(`/api/quotes/items/${itemId}/`, data),
  deleteItem: (itemId: number) => api.delete(`/api/quotes/items/${itemId}/`),

  /** 一键加入报价单（从产品详情页） */
  addItemFromProduct: (quoteId: number, payload: AddItemFromProductPayload) =>
    api.post(`/api/quotes/${quoteId}/items/from-product/`, payload),

  // QT-7/8 分享
  listShares: (quoteId: number) => api.get(`/api/quotes/${quoteId}/shares/`),
  addShare: (quoteId: number, user_id: number) =>
    api.post(`/api/quotes/${quoteId}/shares/`, { user_id }),
  removeShare: (quoteId: number, userId: number) =>
    api.delete(`/api/quotes/${quoteId}/shares/${userId}/`),
};
