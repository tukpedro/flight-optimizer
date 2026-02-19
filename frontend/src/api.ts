// api.ts - API client for the Flight Optimizer backend.

const API_BASE_URL = 'http://localhost:8000/api';

// Types
interface SearchRequest {
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

interface ErrorResponse {
  error: string;
}

export class ApiError extends Error {
  statusCode: number;
  details?: string;

  constructor(message: string, statusCode: number, details?: string) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.details = details;
  }
}

export async function searchFlights(
  fromCity: string,
  toCities: string[]
): Promise<SearchResponse> {
  const payload: SearchRequest = {
    from_city: fromCity,
    to_cities: toCities,
  };

  try {
    const response = await fetch(`${API_BASE_URL}/search/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      const errorData = data as ErrorResponse;
      throw new ApiError(
        errorData.error || 'Request failed',
        response.status,
        JSON.stringify(data)
      );
    }

    return data as SearchResponse;

  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new ApiError(
        'Unable to connect to server. Is the backend running?',
        0,
        'Network error'
      );
    }

    throw new ApiError(
      'An unexpected error occurred',
      0,
      error instanceof Error ? error.message : String(error)
    );
  }
}
