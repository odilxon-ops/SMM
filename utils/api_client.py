import logging
import os
import aiohttp
import api_handler
from config import SMM_API_KEY, SMM_API_URL, SMS_API_KEY, SMS_API_URL
from database.models import db

SMM_KEY_PLACEHOLDERS = {"", "your_smm_api_key_here", "YOUR_SMM_PANEL_API_KEY"}
SMMWIZ_ENV_KEY = os.getenv("SMMWIZ_API_KEY", "").strip()
SMMWIZ_ENV_URL = (os.getenv("SMMWIZ_API_URL") or "https://smmwiz.com/api/v2").strip()
LEGACY_SMM_URL = "https://locksmm.com/api/v2"

class SMMClient:
    def __init__(self, api_key, api_url):
        self.default_api_key = api_key
        self.default_api_url = api_url
        self.timeout = aiohttp.ClientTimeout(total=30)

    async def _get_credentials(self):
        api_key = await db.get_setting("smm_api_key", self.default_api_key)
        api_url = await db.get_setting("smm_api_url", self.default_api_url)
        api_key = (api_key or "").strip()
        api_url = (api_url or "").strip()

        if api_key in SMM_KEY_PLACEHOLDERS and SMMWIZ_ENV_KEY:
            api_key = SMMWIZ_ENV_KEY
            if not api_url or api_url == LEGACY_SMM_URL:
                api_url = SMMWIZ_ENV_URL

        return api_key, api_url

    async def get_services(self, apply_markup=False):
        api_key, api_url = await self._get_credentials()
        return await api_handler.get_services(
            api_key=api_key,
            api_url=api_url,
            apply_markup=apply_markup,
        )

    async def add_order(self, service_id, link, quantity):
        api_key, api_url = await self._get_credentials()
        result = await api_handler.create_order(
            service_id=service_id,
            link=link,
            quantity=quantity,
            api_key=api_key,
            api_url=api_url,
        )
        if isinstance(result, dict) and "order" in result:
            return result["order"]
        return None

    async def check_status(self, order_id):
        api_key, api_url = await self._get_credentials()
        result = await api_handler.get_status(
            order_id=order_id,
            api_key=api_key,
            api_url=api_url,
        )
        if isinstance(result, dict) and "status" in result:
            return result["status"]
        return "Unknown"

    async def get_balance(self):
        api_key, api_url = await self._get_credentials()
        result = await api_handler.get_balance(api_key=api_key, api_url=api_url)
        if isinstance(result, dict) and "balance" in result:
            try:
                balance = float(result["balance"])
            except (TypeError, ValueError):
                balance = 0.0
            return {"balance": balance, "currency": result.get("currency", "USD")}
        return {"balance": 0.0, "currency": "USD"}

class SMSClient:
    def __init__(self, api_key, api_url):
        self.default_api_key = api_key
        self.default_api_url = api_url
        self.timeout = aiohttp.ClientTimeout(total=30)

    async def _get_credentials(self):
        api_key = await db.get_setting("sms_api_key", self.default_api_key)
        api_url = await db.get_setting("sms_api_url", self.default_api_url)
        return api_key, api_url

    async def _request(self, action, **kwargs):
        api_key, api_url = await self._get_credentials()
        params = {"api_key": api_key, "action": action}
        params.update(kwargs)
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(api_url, params=params) as response:
                    return await response.text()
        except Exception as e:
            logging.error(f"SMS API Exception: {e}")
            return f"ERROR:{e}"

    async def get_countries(self, service="tg"):
        api_key, api_url = await self._get_credentials()
        params = {
            "api_key": api_key,
            "action": "getTopCountriesByService",
            "service": service,
            "freePrice": "any",
        }
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(api_url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
        except Exception:
            pass
        # Fallback
        return {
            "0": {"name": "Rossiya", "count": 500, "price": 1500},
            "5": {"name": "O'zbekiston", "count": 200, "price": 2000},
        }

    async def buy_number(self, service, country):
        return await self._request("getNumber", service=service, country=country)

    async def check_sms(self, order_id):
        return await self._request("getStatus", id=order_id)

    async def get_balance(self):
        """SMS API balansini olish"""
        response = await self._request("getBalance")
        if response.startswith("ACCESS_BALANCE:"):
            try:
                balance = float(response.split(":", 1)[1])
                return {"balance": balance, "currency": "RUB"} # sms-activate typically uses RUB
            except (ValueError, IndexError):
                pass
        return {"balance": 0.0, "currency": "RUB"}

    async def set_status(self, order_id, status):
        """
        1 - kodni kutish (tavsiya etilmaydi)
        3 - kodni qayta so'rash
        6 - aktivatsiyani yakunlash
        8 - raqam ishlamadi
        """
        return await self._request("setStatus", id=order_id, status=status)

smm_client = SMMClient(SMM_API_KEY, SMM_API_URL)
sms_client = SMSClient(SMS_API_KEY, SMS_API_URL)
