import api from './api';

export interface RichTextDocumentPayload {
  name: string;
  doc_type?: string;
  folder?: number | null;
  content: string;
  tags?: string[];
}

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

  // 富文本
  createRichText: (payload: RichTextDocumentPayload) =>
    api.post('/api/documents/rich-text/', payload),
  updateRichText: (id: number, payload: Partial<RichTextDocumentPayload>) =>
    api.patch(`/api/documents/${id}/rich-text/`, payload),
};
