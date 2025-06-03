import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

const api = axios.create({
  baseURL: baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Scheme {
  id: number;
  title: string;
  description: string;
  ministry: string;
  category_id: number;
  scheme_type: 'state' | 'central';
  eligibility: string;
  benefits: string;
  documents_required: string;
  application_process: string;
  website: string;
  helpline: string;
  tags: string[];
}

export interface Category {
  id: number;
  name: string;
  description: string;
  icon: string;
  color: string;
  scheme_count?: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
}

export const apiService = {
  // Get all categories with scheme counts
  getCategories: async (): Promise<Category[]> => {
    const response = await api.get('/categories');
    return response.data;
  },

  // Get schemes by category
  getSchemesByCategory: async (
    categoryId: number, 
    page: number = 1, 
    limit: number = 10, 
    sortBy: string = 'relevance'
  ): Promise<PaginatedResponse<Scheme>> => {
    const response = await api.get(`/schemes/category/${categoryId}`, {
      params: {
        page,
        limit,
        sort_by: sortBy,
      },
    });
    return response.data;
  },

  // Get scheme details by ID
  getSchemeDetails: async (schemeId: number): Promise<Scheme> => {
    const response = await api.get(`/schemes/${schemeId}`);
    return response.data;
  },

  // Get schemes by type (State/Central)
  getSchemesByType: async (
    categoryId: number, 
    type: 'state' | 'central', 
    page: number = 1, 
    limit: number = 10
  ): Promise<PaginatedResponse<Scheme>> => {
    const response = await api.get(`/schemes/category/${categoryId}/${type}`, {
      params: {
        page,
        limit,
      },
    });
    return response.data;
  },

  // Search schemes
  searchSchemes: async (
    query: string,
    page: number = 1,
    limit: number = 10
  ): Promise<PaginatedResponse<Scheme>> => {
    const response = await api.get('/search', {
      params: {
        q: query,
        page,
        limit,
      },
    });
    return response.data;
  },
};

export default apiService; 