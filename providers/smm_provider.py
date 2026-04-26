from typing import Any

from providers.base import BaseProvider
from providers.exceptions import ProviderResponseError


class SMMProvider(BaseProvider):
    def __init__(self, api_key: str, api_url: str, timeout_seconds: int = 20):
        super().__init__("SMM provider", api_key, api_url, timeout_seconds)

    def _params(self, action: str, **extra: Any) -> dict[str, Any]:
        params = {"key": self.api_key, "action": action}
        params.update(extra)
        return params

    async def get_services(self) -> list[dict[str, Any]]:
        payload = await self._get_json(self._params("services"))
        if not isinstance(payload, list):
            raise ProviderResponseError("SMM services response must be a list.")
        return payload

    async def get_balance(self) -> dict[str, Any]:
        payload = await self._get_json(self._params("balance"))
        if not isinstance(payload, dict) or "balance" not in payload:
            raise ProviderResponseError("SMM balance response is invalid.")
        return payload

    async def create_order(self, service_id: str, link: str, quantity: int) -> str:
        payload = await self._get_json(
            self._params("add", service=service_id, link=link, quantity=quantity)
        )
        if not isinstance(payload, dict) or "order" not in payload:
            raise ProviderResponseError("SMM order response does not contain order id.")
        return str(payload["order"])

    async def check_status(self, order_id: str) -> dict[str, Any]:
        payload = await self._get_json(self._params("status", order=order_id))
        if not isinstance(payload, dict):
            raise ProviderResponseError("SMM status response is invalid.")
        return payload
