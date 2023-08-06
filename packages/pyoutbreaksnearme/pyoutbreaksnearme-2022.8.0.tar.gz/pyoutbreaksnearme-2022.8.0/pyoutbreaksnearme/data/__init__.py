"""Define data management."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Dict, cast

from pyoutbreaksnearme.util.geo import haversine


class Data:  # pylint: disable=too-few-public-methods
    """Define a manager object for state/coordinate data."""

    def __init__(
        self,
        async_request: Callable[..., Awaitable[dict[str, Any]]],
        nearest_data_endpoint: str,
    ):
        """Initialize."""
        self._async_request = async_request
        self._nearest_data_endpoint = nearest_data_endpoint

    async def async_get_nearest_by_coordinates(
        self, latitude: float, longitude: float
    ) -> dict[str, Any]:
        """Get the nearest CDC to a latitude/longitude."""
        raw_user_report_data = await self._async_request(
            "get", self._nearest_data_endpoint
        )
        feature = min(
            raw_user_report_data["features"],
            key=lambda r: haversine(
                latitude,
                longitude,
                r["geometry"]["coordinates"][1],
                r["geometry"]["coordinates"][0],
            ),
        )
        return cast(Dict[str, Any], feature["properties"])
