import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import FlightResult, SearchRequest, SearchResponse


class TestFlightResult:
    def test_creation(self):
        result = FlightResult(
            destination="Paris",
            destination_code="PAR",
            price=100.0,
            distance_km=344.0,
            price_per_km=0.29,
            fly_from="LHR",
            fly_to="CDG",
        )

        assert result.destination == "Paris"
        assert result.price == 100.0
        assert result.distance_km == 344.0
        assert result.price_per_km == 0.29

    def test_to_dict(self):
        result = FlightResult(
            destination="Berlin",
            destination_code="BER",
            price=80.0,
            distance_km=933.0,
            price_per_km=0.086,
            fly_from="LHR",
            fly_to="BER",
        )

        data = result.to_dict()

        assert isinstance(data, dict)
        assert data["destination"] == "Berlin"
        assert data["price"] == 80.0
        assert "price_per_km" in data


class TestSearchRequest:
    def test_valid_request(self):
        request = SearchRequest(from_city="London", to_cities=["Paris", "Berlin"])
        error = request.validate()
        assert error is None

    def test_empty_from_city(self):
        request = SearchRequest(from_city="", to_cities=["Paris"])
        error = request.validate()
        assert error is not None
        assert "Departure city" in error

    def test_whitespace_from_city(self):
        request = SearchRequest(from_city="   ", to_cities=["Paris"])
        error = request.validate()
        assert error is not None

    def test_empty_to_cities_list(self):
        request = SearchRequest(from_city="London", to_cities=[])
        error = request.validate()
        assert error is not None
        assert "destination" in error.lower()

    def test_only_empty_strings_in_to_cities(self):
        request = SearchRequest(from_city="London", to_cities=["", "  ", ""])
        error = request.validate()
        assert error is not None


class TestSearchResponse:
    def test_creation_with_defaults(self):
        response = SearchResponse(
            best_destination="Paris",
            price_per_km=0.15,
            total_price=50.0,
            distance_km=344.0,
        )

        assert response.currency == "USD"
        assert response.searched_destinations == 0
        assert response.successful_searches == 0

    def test_creation_with_all_fields(self):
        response = SearchResponse(
            best_destination="Berlin",
            price_per_km=0.086,
            total_price=80.0,
            distance_km=933.0,
            currency="USD",
            searched_destinations=3,
            successful_searches=2,
        )

        assert response.searched_destinations == 3
        assert response.successful_searches == 2

    def test_to_dict(self):
        response = SearchResponse(
            best_destination="Paris",
            price_per_km=0.15,
            total_price=50.0,
            distance_km=344.0,
        )

        data = response.to_dict()

        assert isinstance(data, dict)
        assert data["best_destination"] == "Paris"
        assert "currency" in data
