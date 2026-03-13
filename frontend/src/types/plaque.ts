export interface Plaque {
  id: number;
  title: string;
  description?: string;
  inscription?: string;
  latitude: number;
  longitude: number;
  address?: string;
  year_erected?: number;
  organization?: string;
  source_url?: string;
  created_at: string;
  updated_at: string;
  images: Image[];
  categories: Category[];
}

export interface Image {
  id: number;
  plaque_id: number;
  url: string;
  caption?: string;
  photographer?: string;
  year_taken?: number;
  display_order: number;
  created_at: string;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
}

export interface PlaqueListResponse {
  total: number;
  page: number;
  page_size: number;
  plaques: Plaque[];
}
