import api from './api';

export const catalogService = {
  /** 图册浏览（多维筛选） */
  getCatalog: (params?: any) => api.get('/api/catalog/', { params }),

  /** 图册关键词搜索 */
  searchCatalog: (params?: any) => api.get('/api/catalog/search/', { params }),

  /** 筛选项聚合（品牌/类别/产地/货期/MECE/动态属性） */
  getFilters: () => api.get('/api/catalog/filters/'),
};
