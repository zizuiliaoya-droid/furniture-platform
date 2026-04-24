import api from './api';

export const searchService = {
  search: (q: string) => api.get('/api/search/', { params: { q } }),
};
