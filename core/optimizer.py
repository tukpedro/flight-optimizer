import logging
from typing import Optional
from .models import FlightResult, SearchRequest, SearchResponse, FlightSummary
from .kiwi_client import KiwiClient, CityNotFoundError, NoFlightsError, KiwiAPIError

logger = logging.getLogger(__name__)


class FlightOptimizer:
    def __init__(self, client: KiwiClient):
        self.client = client

    @staticmethod
    def calculate_price_per_km(price: float, distance_km: float) -> float:
        if distance_km <= 0:
            return float('inf')
        return price / distance_km

    def search_single_destination(
        self,
        from_code: str,
        to_city: str,
    ) -> Optional[tuple[FlightResult, str]]:
        try:
            dest_info = self.client.get_city_code(to_city)
            flight = self.client.search_flights(from_code, dest_info.code)

            price = flight.get("price", 0)
            distance = flight.get("distance", 0)
            price_per_km = self.calculate_price_per_km(price, distance)

            result = FlightResult(
                destination=flight.get("cityTo", dest_info.name),
                destination_code=dest_info.code,
                price=price,
                distance_km=distance,
                price_per_km=price_per_km,
                fly_from=flight.get("flyFrom", from_code),
                fly_to=flight.get("flyTo", dest_info.code),
            )
            return (result, dest_info.country)

        except CityNotFoundError:
            logger.warning(f"City not found: {to_city}")
            return None

        except NoFlightsError:
            logger.warning(f"No flights from {from_code} to {to_city}")
            return None

        except KiwiAPIError as e:
            logger.error(f"API error searching {to_city}: {e}")
            return None

    def find_best_flight(self, request: SearchRequest) -> SearchResponse:
        validation_error = request.validate()
        if validation_error:
            raise ValueError(validation_error)

        to_cities = [city.strip() for city in request.to_cities if city.strip()]
        from_info = self.client.get_city_code(request.from_city)

        results: list[tuple[FlightResult, str]] = []

        for city in to_cities:
            search_result = self.search_single_destination(from_info.code, city)
            if search_result is not None:
                results.append(search_result)

        if not results:
            raise ValueError(
                f"No flights available from {request.from_city} "
                f"to any of the specified destinations"
            )

        sorted_results = sorted(results, key=lambda r: r[0].price_per_km)
        best_result, best_country = sorted_results[0]

        all_results = [
            FlightSummary(
                destination=flight.destination,
                country=country,
                price_per_km=round(flight.price_per_km, 4),
                total_price=flight.price,
                distance_km=flight.distance_km,
                is_best=(flight.destination == best_result.destination),
            )
            for flight, country in sorted_results
        ]

        return SearchResponse(
            best_destination=best_result.destination,
            price_per_km=round(best_result.price_per_km, 4),
            total_price=best_result.price,
            distance_km=best_result.distance_km,
            from_city=from_info.name,
            from_country=from_info.country,
            to_country=best_country,
            currency="USD",
            searched_destinations=len(to_cities),
            successful_searches=len(results),
            all_results=all_results,
        )

    def find_all_flights_sorted(self, request: SearchRequest) -> list[FlightResult]:
        validation_error = request.validate()
        if validation_error:
            raise ValueError(validation_error)

        to_cities = [city.strip() for city in request.to_cities if city.strip()]
        from_info = self.client.get_city_code(request.from_city)

        results: list[FlightResult] = []
        for city in to_cities:
            result = self.search_single_destination(from_info.code, city)
            if result is not None:
                flight_result, _ = result
                results.append(flight_result)

        return sorted(results, key=lambda r: r.price_per_km)
