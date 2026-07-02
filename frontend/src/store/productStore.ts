import { create } from 'zustand';
import { productService } from '../services/productService';

interface ProductState {
  products: any[];
  total: number;
  loading: boolean;
  filters: {
    search?: string; origin?: string; category?: number; is_active?: string;
    category_l1?: string; category_l2?: string; brand?: number; lead_time?: string;
    min_price?: number; max_price?: number;
  };
  page: number;
  pageSize: number;
  fetchProducts: () => Promise<void>;
  setFilters: (filters: Partial<ProductState['filters']>) => void;
  resetFilters: () => void;
  setPage: (page: number) => void;
}

export const useProductStore = create<ProductState>((set, get) => ({
  products: [],
  total: 0,
  loading: false,
  filters: {},
  page: 1,
  pageSize: 20,

  fetchProducts: async () => {
    set({ loading: true });
    try {
      const { filters, page, pageSize } = get();
      const params = { ...filters, page, page_size: pageSize };
      const { data } = await productService.getProducts(params);
      set({ products: data.results, total: data.count });
    } finally {
      set({ loading: false });
    }
  },

  setFilters: (filters) => {
    set((state) => ({ filters: { ...state.filters, ...filters }, page: 1 }));
    get().fetchProducts();
  },

  resetFilters: () => {
    set({ filters: {}, page: 1 });
    get().fetchProducts();
  },

  setPage: (page) => {
    set({ page });
    get().fetchProducts();
  },
}));
