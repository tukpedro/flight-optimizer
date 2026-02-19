import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core import KiwiClient


SAMPLE_LOCATION_LONDON = {
    "locations": [
        {
            "id": "london_gb",
            "code": "LON",
            "name": "London",
            "location": {"lat": "51.507351", "lon": "-0.127758"},
            "type": "city"
        }
    ]
}

SAMPLE_LOCATION_PARIS = {
    "locations": [
        {
            "id": "paris_fr",
            "code": "PAR",
            "name": "Paris",
            "location": {"lat": "48.856614", "lon": "2.352222"},
            "type": "city"
        }
    ]
}

SAMPLE_LOCATION_BERLIN = {
    "locations": [
        {
            "id": "berlin_de",
            "code": "BER",
            "name": "Berlin",
            "location": {"lat": "52.520008", "lon": "13.404954"},
            "type": "city"
        }
    ]
}

SAMPLE_FLIGHT_LONDON_PARIS = {
    "data": [
        {
            "id": "abc123",
            "price": 50,
            "distance": 344.0,
            "flyFrom": "LHR",
            "flyTo": "CDG",
            "cityFrom": "London",
            "cityTo": "Paris",
        }
    ]
}

SAMPLE_FLIGHT_LONDON_BERLIN = {
    "data": [
        {
            "id": "def456",
            "price": 80,
            "distance": 933.0,
            "flyFrom": "LHR",
            "flyTo": "BER",
            "cityFrom": "London",
            "cityTo": "Berlin",
        }
    ]
}

SAMPLE_NO_FLIGHTS = {"data": []}


@pytest.fixture
def api_key():
    return "test-api-key-12345"


@pytest.fixture
def mock_session():
    with patch('core.kiwi_client.requests.Session') as mock:
        session_instance = Mock()
        mock.return_value = session_instance
        yield session_instance


@pytest.fixture
def kiwi_client(api_key, mock_session):
    client = KiwiClient(api_key)
    return client


@pytest.fixture
def sample_locations():
    return {
        "london": SAMPLE_LOCATION_LONDON,
        "paris": SAMPLE_LOCATION_PARIS,
        "berlin": SAMPLE_LOCATION_BERLIN,
    }


@pytest.fixture
def sample_flights():
    return {
        "london_paris": SAMPLE_FLIGHT_LONDON_PARIS,
        "london_berlin": SAMPLE_FLIGHT_LONDON_BERLIN,
        "no_flights": SAMPLE_NO_FLIGHTS,
    }
