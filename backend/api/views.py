from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import logging

from core import (
    KiwiClient,
    FlightOptimizer,
    SearchRequest,
    CityNotFoundError,
    KiwiAPIError,
)

logger = logging.getLogger(__name__)


class FlightSearchView(APIView):
    def post(self, request):
        from_city = request.data.get('from_city', '').strip()
        to_cities = request.data.get('to_cities', [])

        if not from_city:
            return Response(
                {'error': 'from_city is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not to_cities or not isinstance(to_cities, list):
            return Response(
                {'error': 'to_cities must be a non-empty list'},
                status=status.HTTP_400_BAD_REQUEST
            )

        to_cities = [city.strip() for city in to_cities if isinstance(city, str) and city.strip()]

        if not to_cities:
            return Response(
                {'error': 'to_cities must contain at least one valid city'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with KiwiClient(settings.KIWI_API_KEY) as client:
                optimizer = FlightOptimizer(client)
                search_request = SearchRequest(from_city=from_city, to_cities=to_cities)
                result = optimizer.find_best_flight(search_request)
                return Response(result.to_dict(), status=status.HTTP_200_OK)

        except CityNotFoundError as e:
            return Response(
                {'error': f"City not found: {e.city_name}"},
                status=status.HTTP_404_NOT_FOUND
            )

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except KiwiAPIError:
            return Response(
                {'error': 'External API error. Please try again later.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
