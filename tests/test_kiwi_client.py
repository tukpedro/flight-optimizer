import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.kiwi_client import KiwiClient, KiwiAPIError, CityNotFoundError, NoFlightsError


class TestKiwiClientInit:
    def test_creates_session_with_headers(self):
        with patch('core.kiwi_client.requests.Session') as mock_session:
            client = KiwiClient("test-api-key")
            mock_session.return_value.headers.update.assert_called_once()
            call_args = mock_session.return_value.headers.update.call_args[0][0]
            assert call_args["apikey"] == "test-api-key"

    def test_custom_timeout(self):
        with patch('core.kiwi_client.requests.Session'):
            client = KiwiClient("test-key", timeout=60)
            assert client.timeout == 60


class TestGetCityCode:
    @pytest.fixture
    def client(self):
        with patch('core.kiwi_client.requests.Session') as mock_session:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "locations": [
                    {
                        "code": "LON",
                        "name": "London",
                        "location": {"lat": "51.5", "lon": "-0.1"}
                    }
                ]
            }
            mock_session.return_value.get.return_value = mock_response
            client = KiwiClient("test-key")
            yield client

    def test_returns_location_info(self, client):
        result = client.get_city_code("London")
        assert result.code == "LON"
        assert result.name == "London"
        assert result.latitude == 51.5

    def test_raises_city_not_found_for_empty_results(self):
        with patch('core.kiwi_client.requests.Session') as mock_session:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"locations": []}
            mock_session.return_value.get.return_value = mock_response
            client = KiwiClient("test-key")

            with pytest.raises(CityNotFoundError) as exc_info:
                client.get_city_code("NonexistentCity")
            assert exc_info.value.city_name == "NonexistentCity"


class TestSearchFlights:
    def test_returns_flight_data(self):
        with patch('core.kiwi_client.requests.Session') as mock_session:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": [
                    {
                        "price": 50,
                        "distance": 344,
                        "cityTo": "Paris",
                        "flyFrom": "LHR",
                        "flyTo": "CDG",
                    }
                ]
            }
            mock_session.return_value.get.return_value = mock_response
            client = KiwiClient("test-key")

            result = client.search_flights("LON", "PAR")

            assert result["price"] == 50
            assert result["distance"] == 344
            assert result["cityTo"] == "Paris"

    def test_raises_no_flights_for_empty_data(self):
        with patch('core.kiwi_client.requests.Session') as mock_session:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": []}
            mock_session.return_value.get.return_value = mock_response
            client = KiwiClient("test-key")

            with pytest.raises(NoFlightsError) as exc_info:
                client.search_flights("LON", "XYZ")
            assert exc_info.value.from_city == "LON"
            assert exc_info.value.to_city == "XYZ"


class TestErrorHandling:
    def test_handles_rate_limit(self):
        with patch('core.kiwi_client.requests.Session') as mock_session:
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.text = "Rate limit exceeded"
            mock_session.return_value.get.return_value = mock_response
            client = KiwiClient("test-key")

            with pytest.raises(KiwiAPIError, match="Rate limit"):
                client.get_city_code("London")

    def test_handles_server_error(self):
        with patch('core.kiwi_client.requests.Session') as mock_session:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal server error"
            mock_session.return_value.get.return_value = mock_response
            client = KiwiClient("test-key")

            with pytest.raises(KiwiAPIError, match="Server error"):
                client.get_city_code("London")

    def test_handles_timeout(self):
        with patch('core.kiwi_client.requests.Session') as mock_session:
            mock_session.return_value.get.side_effect = requests.exceptions.Timeout()
            client = KiwiClient("test-key")

            with pytest.raises(KiwiAPIError, match="timeout"):
                client.get_city_code("London")

    def test_handles_connection_error(self):
        with patch('core.kiwi_client.requests.Session') as mock_session:
            mock_session.return_value.get.side_effect = requests.exceptions.ConnectionError()
            client = KiwiClient("test-key")

            with pytest.raises(KiwiAPIError, match="Connection error"):
                client.get_city_code("London")


class TestContextManager:
    def test_context_manager_closes_session(self):
        with patch('core.kiwi_client.requests.Session') as mock_session:
            mock_instance = Mock()
            mock_session.return_value = mock_instance

            with KiwiClient("test-key") as client:
                pass

            mock_instance.close.assert_called_once()
