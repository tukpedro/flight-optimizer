from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class FlightResult:
    destination: str
    destination_code: str
    price: float
    distance_km: float
    price_per_km: float
    fly_from: str
    fly_to: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SearchRequest:
    from_city: str
    to_cities: list[str]

    def validate(self) -> Optional[str]:
        if not self.from_city or not self.from_city.strip():
            return "Departure city is required"

        if not self.to_cities or len(self.to_cities) == 0:
            return "At least one destination city is required"

        valid_destinations = [city for city in self.to_cities if city.strip()]
        if len(valid_destinations) == 0:
            return "At least one valid destination city is required"

        return None


@dataclass
class FlightSummary:
    destination: str
    country: str
    price_per_km: float
    total_price: float
    distance_km: float
    is_best: bool = False


@dataclass
class SearchResponse:
    best_destination: str
    price_per_km: float
    total_price: float
    distance_km: float
    from_city: str = ""
    from_country: str = ""
    to_country: str = ""
    currency: str = "USD"
    searched_destinations: int = 0
    successful_searches: int = 0
    all_results: list[FlightSummary] = None  # type: ignore

    def __post_init__(self):
        if self.all_results is None:
            self.all_results = []

    def to_dict(self) -> dict:
        result = asdict(self)
        result['all_results'] = [asdict(r) for r in self.all_results]
        return result


@dataclass
class LocationInfo:
    code: str
    name: str
    country: str
    latitude: float
    longitude: float
