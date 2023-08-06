"""Define user data."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from pyoutbreaksnearme.data import Data


class UserData(Data):  # pylint: disable=too-few-public-methods
    """Define a manager object for state/coordinate data."""

    def __init__(self, async_request: Callable[..., Awaitable[dict[str, Any]]]):
        """Initialize."""
        super().__init__(async_request, "markers/US")

    async def async_get_totals(self) -> dict[str, Any]:
        """Get user report totals."""
        tasks = [
            self._async_request("get", "usersubmission/stats/region/NOA"),
            self._async_request("get", "stats/US"),
        ]
        results = await asyncio.gather(*tasks)
        return {**results[0], **results[1]}
