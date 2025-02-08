import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface StancePrediction {
  target: string
  target_type: string
  stance: string
  justification?: string
}

export interface Blogger {
  name: string
  profile_url: string
}

export interface Category {
  name: string
}

export interface Article {
  id: number
  title: string
  content: string
  article_url: string
  published_date?: string
  blogger: Blogger
  categories: Category[]
  stance_predictions: StancePrediction[]
}

interface GetArticlesParams {
  skip?: number
  limit?: number
  target?: string
  target_type?: string
  stance?: string
}

export const api = {
  articles: {
    getAll: async (params: GetArticlesParams = {}): Promise<Article[]> => {
      const { data } = await axios.get(`${API_BASE_URL}/api/v1/articles`, { params })
      return data
    },
  },
} 