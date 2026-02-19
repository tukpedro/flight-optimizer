// types.ts
// TypeScript type definitions for the Flight Optimizer frontend.

export interface SearchRequest {
  from_city: string;
  to_cities: string[];
}

export interface FlightSummary {
  destination: string;
  country: string;
  price_per_km: number;
  total_price: number;
  distance_km: number;
  is_best: boolean;
}

export interface SearchResponse {
  best_destination: string;
  price_per_km: number;
  total_price: number;
  distance_km: number;
  from_city: string;
  from_country: string;
  to_country: string;
  currency: string;
  searched_destinations: number;
  successful_searches: number;
  all_results: FlightSummary[];
}

export interface ErrorResponse {
  error: string;
}

export interface FormState {
  fromCity: string;
  toCities: string;
  loading: boolean;
  error: string | null;
  result: SearchResponse | null;
}
