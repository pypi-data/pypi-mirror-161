"""Define CDC data."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from pyoutbreaksnearme.data import Data


class CDCData(Data):  # pylint: disable=too-few-public-methods
    """Define a manager object for state/coordinate data."""

    def __init__(self, async_request: Callable[..., Awaitable[dict[str, Any]]]):
        """Initialize."""
        super().__init__(async_request, "nonuserstats/US")
