import api from './api';

export const documentService = {
  getDocuments: (params?: any) => api.get('/api/documents/', { params }),
  uploadDocument: (formData: FormData) =>
    api.post('/api/documents/upload/', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  deleteDocument: (id: number) => api.delete(`/api/documents/${id}/`),
  downloadDocument: (id: number) => api.get(`/api/documents/${id}/download/`, { responseType: 'blob' }),
  updateTags: (id: number, tags: string[]) => api.patch(`/api/documents/${id}/tags/`, { tags }),
  getFolders: (params?: any) => api.get('/api/document-folders/', { params }),
  getFolderTree: (docType?: string) => api.get('/api/document-folders/tree/', { params: { doc_type: docType } }),
  createFolder: (data: any) => api.post('/api/document-folders/', data),
  deleteFolder: (id: number) => api.delete(`/api/document-folders/${id}/`),
};
