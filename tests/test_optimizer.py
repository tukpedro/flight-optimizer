import pytest
from unittest.mock import Mock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.optimizer import FlightOptimizer
from core.kiwi_client import KiwiClient, CityNotFoundError, NoFlightsError
from core.models import SearchRequest, FlightResult, LocationInfo


class TestCalculatePricePerKm:
    def test_normal_calculation(self):
        result = FlightOptimizer.calculate_price_per_km(100.0, 500.0)
        assert result == 0.2

    def test_zero_distance_returns_infinity(self):
        result = FlightOptimizer.calculate_price_per_km(100.0, 0.0)
        assert result == float('inf')

    def test_negative_distance_returns_infinity(self):
        result = FlightOptimizer.calculate_price_per_km(100.0, -10.0)
        assert result == float('inf')

    def test_very_small_distance(self):
        result = FlightOptimizer.calculate_price_per_km(50.0, 0.1)
        assert result == 500.0

    def test_zero_price(self):
        result = FlightOptimizer.calculate_price_per_km(0.0, 100.0)
        assert result == 0.0


class TestFindBestFlight:
    @pytest.fixture
    def mock_client(self):
        return Mock(spec=KiwiClient)

    @pytest.fixture
    def optimizer(self, mock_client):
        return FlightOptimizer(mock_client)

    def test_finds_best_flight_by_price_per_km(self, optimizer, mock_client):
        mock_client.get_city_code.side_effect = [
            LocationInfo("LON", "London", "United Kingdom", 51.5, -0.1),
            LocationInfo("PAR", "Paris", "France", 48.9, 2.3),
            LocationInfo("BER", "Berlin", "Germany", 52.5, 13.4),
        ]

        mock_client.search_flights.side_effect = [
            {"price": 50, "distance": 344, "cityTo": "Paris", "flyFrom": "LHR", "flyTo": "CDG"},
            {"price": 80, "distance": 933, "cityTo": "Berlin", "flyFrom": "LHR", "flyTo": "BER"},
        ]

        request = SearchRequest(from_city="London", to_cities=["Paris", "Berlin"])
        response = optimizer.find_best_flight(request)

        assert response.best_destination == "Berlin"
        assert response.price_per_km < 0.1

    def test_handles_invalid_departure_city(self, optimizer, mock_client):
        mock_client.get_city_code.side_effect = CityNotFoundError("InvalidCity")
        request = SearchRequest(from_city="InvalidCity", to_cities=["Paris"])

        with pytest.raises(CityNotFoundError):
            optimizer.find_best_flight(request)

    def test_handles_no_flights_to_destination(self, optimizer, mock_client):
        mock_client.get_city_code.side_effect = [
            LocationInfo("LON", "London", "United Kingdom", 51.5, -0.1),
            LocationInfo("PAR", "Paris", "France", 48.9, 2.3),
            LocationInfo("BER", "Berlin", "Germany", 52.5, 13.4),
        ]

        mock_client.search_flights.side_effect = [
            NoFlightsError("LON", "PAR"),
            {"price": 80, "distance": 933, "cityTo": "Berlin", "flyFrom": "LHR", "flyTo": "BER"},
        ]

        request = SearchRequest(from_city="London", to_cities=["Paris", "Berlin"])
        response = optimizer.find_best_flight(request)

        assert response.best_destination == "Berlin"
        assert response.successful_searches == 1
        assert response.searched_destinations == 2

    def test_handles_all_destinations_failing(self, optimizer, mock_client):
        mock_client.get_city_code.side_effect = [
            LocationInfo("LON", "London", "United Kingdom", 51.5, -0.1),
            LocationInfo("PAR", "Paris", "France", 48.9, 2.3),
        ]

        mock_client.search_flights.side_effect = NoFlightsError("LON", "PAR")
        request = SearchRequest(from_city="London", to_cities=["Paris"])

        with pytest.raises(ValueError, match="No flights available"):
            optimizer.find_best_flight(request)

    def test_validates_request(self, optimizer, mock_client):
        request = SearchRequest(from_city="", to_cities=["Paris"])

        with pytest.raises(ValueError, match="Departure city"):
            optimizer.find_best_flight(request)


class TestFindAllFlightsSorted:
    @pytest.fixture
    def mock_client(self):
        return Mock(spec=KiwiClient)

    @pytest.fixture
    def optimizer(self, mock_client):
        return FlightOptimizer(mock_client)

    def test_returns_sorted_results(self, optimizer, mock_client):
        mock_client.get_city_code.side_effect = [
            LocationInfo("LON", "London", "United Kingdom", 51.5, -0.1),
            LocationInfo("PAR", "Paris", "France", 48.9, 2.3),
            LocationInfo("BER", "Berlin", "Germany", 52.5, 13.4),
            LocationInfo("MAD", "Madrid", "Spain", 40.4, -3.7),
        ]

        mock_client.search_flights.side_effect = [
            {"price": 50, "distance": 344, "cityTo": "Paris", "flyFrom": "LHR", "flyTo": "CDG"},
            {"price": 80, "distance": 933, "cityTo": "Berlin", "flyFrom": "LHR", "flyTo": "BER"},
            {"price": 120, "distance": 1264, "cityTo": "Madrid", "flyFrom": "LHR", "flyTo": "MAD"},
        ]

        request = SearchRequest(from_city="London", to_cities=["Paris", "Berlin", "Madrid"])
        results = optimizer.find_all_flights_sorted(request)

        assert len(results) == 3
        assert results[0].destination == "Berlin"
        assert results[1].destination == "Madrid"
        assert results[2].destination == "Paris"

        for i in range(len(results) - 1):
            assert results[i].price_per_km <= results[i + 1].price_per_km
