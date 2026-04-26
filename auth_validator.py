import hmac
import hashlib
import logging
import time
from urllib.parse import parse_qsl
from config import BOT_TOKEN, MINI_APP_AUTH_MAX_AGE

logger = logging.getLogger(__name__)

def validate_telegram_data(init_data: str) -> bool:
    """
    Telegram Mini App dan kelgan initData ni xavfsizlik tekshiruvidan o'tkazish.
    """
    try:
        if not BOT_TOKEN:
            return False

        # parse_qsl qiymatlarda '=' yoki URL kodlangan belgilar bo'lsa ham to'g'ri ajratadi.
        parsed_data = dict(parse_qsl(init_data, keep_blank_values=True))
        
        # Hashni ajratib olamiz
        received_hash = parsed_data.pop('hash')

        auth_date = int(parsed_data.get("auth_date", "0"))
        current_time = int(time.time())

        if auth_date <= 0:
            return False
        if auth_date > current_time + 30:
            return False
        if current_time - auth_date > MINI_APP_AUTH_MAX_AGE:
            return False
        
        # Qolgan parametrlarni alfavit tartibida taxlaymiz va string yaratamiz
        sorted_keys = sorted(parsed_data.keys())
        data_check_string = '\n'.join([f"{key}={parsed_data[key]}" for key in sorted_keys])
        
        # Secret key yaratish (WebAppData)
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        
        # Yaratilgan secret_key bilan data_check_string ni hashlash
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        # Hashlarni solishtirish
        return hmac.compare_digest(calculated_hash, received_hash)
        
    except Exception as e:
        logger.warning("Auth validation error: %s", e)
        return False
