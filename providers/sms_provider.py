from typing import Any

from providers.base import BaseProvider
from providers.exceptions import ProviderResponseError


class SMSProvider(BaseProvider):
    def __init__(self, api_key: str, api_url: str, timeout_seconds: int = 20):
        super().__init__("SMS provider", api_key, api_url, timeout_seconds)

    def _params(self, action: str, **extra: Any) -> dict[str, Any]:
        params = {"api_key": self.api_key, "action": action}
        params.update(extra)
        return params

    async def get_countries(self, service: str = "tg") -> dict[str, Any]:
        payload = await self._get_json(
            self._params("getTopCountriesByService", service=service, freePrice="any")
        )
        if not isinstance(payload, dict):
            raise ProviderResponseError("SMS countries response must be a JSON object.")
        return payload

    async def buy_number(self, service: str, country: str) -> str:
        payload = await self._get_text(self._params("getNumber", service=service, country=country))
        if not payload or payload.startswith("ERROR"):
            raise ProviderResponseError(f"SMS buy_number failed: {payload or 'empty response'}")
        return payload

    async def get_balance(self) -> dict[str, Any]:
        payload = await self._get_text(self._params("getBalance"))
        if not payload.startswith("ACCESS_BALANCE:"):
            raise ProviderResponseError(f"SMS balance response is invalid: {payload}")
        return {
            "balance": payload.split(":", 1)[1],
            "currency": "RUB",
        }

    async def get_status(self, order_id: str) -> str:
        payload = await self._get_text(self._params("getStatus", id=order_id))
        if not payload:
            raise ProviderResponseError("SMS status response is empty.")
        return payload
