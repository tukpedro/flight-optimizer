import requests
from datetime import datetime, timedelta
from typing import Optional
from .models import LocationInfo


class KiwiAPIError(Exception):
    pass


class CityNotFoundError(KiwiAPIError):
    def __init__(self, city_name: str):
        self.city_name = city_name
        super().__init__(f"City not found: {city_name}")


class NoFlightsError(KiwiAPIError):
    def __init__(self, from_city: str, to_city: str):
        self.from_city = from_city
        self.to_city = to_city
        super().__init__(f"No flights available from {from_city} to {to_city}")


class KiwiClient:
    BASE_URL = "https://tequila-api.kiwi.com"

    def __init__(self, api_key: str, timeout: int = 30):
        self.api_key = api_key
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "apikey": self.api_key,
            "Content-Type": "application/json",
        })

    def _get(self, endpoint: str, params: dict) -> dict:
        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = self._session.get(url, params=params, timeout=self.timeout)

            if response.status_code == 400:
                raise KiwiAPIError(f"Bad request: {response.text}")
            elif response.status_code == 401:
                raise KiwiAPIError("Invalid API key")
            elif response.status_code == 404:
                raise KiwiAPIError(f"Endpoint not found: {endpoint}")
            elif response.status_code == 429:
                raise KiwiAPIError("Rate limit exceeded")
            elif response.status_code >= 500:
                raise KiwiAPIError(f"Server error: {response.status_code}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            raise KiwiAPIError(f"Request timeout after {self.timeout}s")
        except requests.exceptions.ConnectionError:
            raise KiwiAPIError("Connection error - check network")
        except requests.exceptions.JSONDecodeError:
            raise KiwiAPIError("Invalid JSON response from API")

    def get_city_code(self, city_name: str) -> LocationInfo:
        params = {
            "term": city_name,
            "location_types": "city",
            "limit": 1,
            "active_only": "true",
        }

        data = self._get("/locations/query", params)

        locations = data.get("locations", [])
        if not locations:
            raise CityNotFoundError(city_name)

        location = locations[0]
        loc_coords = location.get("location", {})
        country_data = location.get("country", {})
        country_name = country_data.get("name", "") if isinstance(country_data, dict) else ""

        return LocationInfo(
            code=location.get("code", location.get("id", "")),
            name=location.get("name", city_name),
            country=country_name,
            latitude=float(loc_coords.get("lat", 0)),
            longitude=float(loc_coords.get("lon", 0)),
        )

    def search_flights(
        self,
        from_code: str,
        to_code: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> dict:
        if date_from is None:
            date_from = datetime.now().strftime("%d/%m/%Y")
        if date_to is None:
            date_to = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")

        params = {
            "fly_from": from_code,
            "fly_to": to_code,
            "date_from": date_from,
            "date_to": date_to,
            "curr": "USD",
            "adults": 1,
            "limit": 1,
            "sort": "price",
            "asc": 1,
        }

        data = self._get("/v2/search", params)

        flights = data.get("data", [])
        if not flights:
            raise NoFlightsError(from_code, to_code)

        return flights[0]

    def close(self):
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
