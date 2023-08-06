"""Define an API client."""
from __future__ import annotations

from typing import Any, Dict, cast

from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError

from pyoutbreaksnearme.const import LOGGER
from pyoutbreaksnearme.data.cdc import CDCData
from pyoutbreaksnearme.data.user import UserData
from pyoutbreaksnearme.errors import RequestError

API_HOST = "outbreaksnearme.org"
API_URL_BASE = f"https://{API_HOST}/api"

DEFAULT_TIMEOUT = 10
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, "
    "like Gecko) Chrome/103.0.5060.134 Safari/537.36"
)


class Client:  # pylint: disable=too-few-public-methods
    """Define the client."""

    def __init__(self, *, session: ClientSession | None = None) -> None:
        """Initialize."""
        self._session = session
        self.cdc_data = CDCData(self._async_request)
        self.user_data = UserData(self._async_request)

    async def _async_request(
        self, method: str, endpoint: str, **kwargs: dict[str, Any]
    ) -> dict[str, Any]:
        """Make a request against Flu Near You."""
        kwargs.setdefault("headers", {})
        kwargs["headers"].update({"Host": API_HOST, "User-Agent": DEFAULT_USER_AGENT})

        use_running_session = self._session and not self._session.closed

        if use_running_session:
            session = self._session
        else:
            session = ClientSession(timeout=ClientTimeout(total=DEFAULT_TIMEOUT))

        assert session

        try:
            async with session.request(
                method, f"{API_URL_BASE}/{endpoint}", **kwargs
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
        except ClientError as err:
            raise RequestError(
                f"Error requesting data from {endpoint}: {err}"
            ) from None
        finally:
            if not use_running_session:
                await session.close()

        LOGGER.debug("Data returned for /%s: %s", endpoint, data)

        return cast(Dict[str, Any], data)
