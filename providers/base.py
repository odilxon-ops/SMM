import asyncio
from typing import Any

import aiohttp

from providers.exceptions import (
    ProviderAuthError,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)


class BaseProvider:
    def __init__(self, provider_name: str, api_key: str, api_url: str, timeout_seconds: int = 20):
        self.provider_name = provider_name
        self.api_key = api_key
        self.api_url = api_url
        self.timeout = aiohttp.ClientTimeout(total=timeout_seconds)

    def _ensure_configured(self) -> None:
        if not self.api_key or not self.api_url:
            raise ProviderAuthError(f"{self.provider_name} credentials are not configured.")

    async def _get_json(self, params: dict[str, Any]) -> Any:
        self._ensure_configured()
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(self.api_url, params=params) as response:
                    self._raise_for_status(response.status)
                    try:
                        return await response.json(content_type=None)
                    except Exception as exc:  # pragma: no cover - defensive parsing
                        body = await response.text()
                        raise ProviderResponseError(
                            f"{self.provider_name} JSON parse failed: {body[:200]}"
                        ) from exc
        except asyncio.TimeoutError as exc:
            raise ProviderTimeoutError(f"{self.provider_name} request timed out.") from exc
        except aiohttp.ClientError as exc:
            raise ProviderUnavailableError(f"{self.provider_name} is unavailable.") from exc

    async def _get_text(self, params: dict[str, Any]) -> str:
        self._ensure_configured()
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(self.api_url, params=params) as response:
                    self._raise_for_status(response.status)
                    return await response.text()
        except asyncio.TimeoutError as exc:
            raise ProviderTimeoutError(f"{self.provider_name} request timed out.") from exc
        except aiohttp.ClientError as exc:
            raise ProviderUnavailableError(f"{self.provider_name} is unavailable.") from exc

    @staticmethod
    def _raise_for_status(status_code: int) -> None:
        if status_code in (401, 403):
            raise ProviderAuthError(f"Provider auth failed with HTTP {status_code}.")
        if status_code >= 500:
            raise ProviderUnavailableError(f"Provider returned HTTP {status_code}.")
        if status_code >= 400:
            raise ProviderResponseError(f"Provider returned HTTP {status_code}.")
