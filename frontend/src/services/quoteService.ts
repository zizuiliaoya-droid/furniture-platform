import api from './api';

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
  updateItem: (itemId: number, data: any) => api.put(`/api/quotes/items/${itemId}/`, data),
  deleteItem: (itemId: number) => api.delete(`/api/quotes/items/${itemId}/`),
};
