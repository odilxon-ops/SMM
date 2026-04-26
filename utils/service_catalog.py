import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from urllib.parse import urlparse


PLATFORM_META = {
    "telegram": {"label": "Telegram", "emoji": "✈️", "sort_order": 10},
    "instagram": {"label": "Instagram", "emoji": "📸", "sort_order": 20},
    "special": {"label": "Maxsus", "emoji": "🎁", "sort_order": 30},
    "bonus": {"label": "Bonuslar", "emoji": "💎", "sort_order": 40},
}


GROUP_META = {
    "tg_premium": {
        "platform_key": "telegram",
        "label": "Premium obunachilar",
        "emoji": "👑",
        "sort_order": 10,
    },
    "tg_uzbek": {
        "platform_key": "telegram",
        "label": "O'zbek obunachilar",
        "emoji": "🇺🇿",
        "sort_order": 20,
    },
    "tg_boost": {
        "platform_key": "telegram",
        "label": "BOOST ovozlar",
        "emoji": "🚀",
        "sort_order": 30,
    },
    "tg_reactions": {
        "platform_key": "telegram",
        "label": "Avto-reaksiyalar",
        "emoji": "🔥",
        "sort_order": 40,
    },
    "tg_views": {
        "platform_key": "telegram",
        "label": "Post ko'rishlar",
        "emoji": "👀",
        "sort_order": 50,
    },
    "ig_followers": {
        "platform_key": "instagram",
        "label": "Obunachi",
        "emoji": "👥",
        "sort_order": 55,
    },
    "ig_reels": {
        "platform_key": "instagram",
        "label": "Reels",
        "emoji": "🎬",
        "sort_order": 60,
    },
    "ig_likes": {
        "platform_key": "instagram",
        "label": "Layk",
        "emoji": "❤️",
        "sort_order": 70,
    },
    "gift_items": {
        "platform_key": "special",
        "label": "Gift hadiyalar",
        "emoji": "🎁",
        "sort_order": 80,
    },
    "bonus_free": {
        "platform_key": "bonus",
        "label": "Tekin bonuslar",
        "emoji": "💎",
        "sort_order": 90,
    },
}


COUNTRY_FLAGS = {
    "uzbekistan": "🇺🇿",
    "uzbek": "🇺🇿",
    "russia": "🇷🇺",
    "rus": "🇷🇺",
    "rossiya": "🇷🇺",
    "kazakhstan": "🇰🇿",
    "qozog": "🇰🇿",
    "kazakh": "🇰🇿",
    "usa": "🇺🇸",
    "united states": "🇺🇸",
    "us": "🇺🇸",
    "turkey": "🇹🇷",
    "turkiye": "🇹🇷",
    "india": "🇮🇳",
    "ukraine": "🇺🇦",
    "ua": "🇺🇦",
}


def normalize_text(*parts):
    text = " ".join(str(part or "") for part in parts).casefold()
    replacements = {
        "oʻ": "o",
        "o'": "o",
        "gʻ": "g",
        "g'": "g",
        "’": "",
        "-": " ",
        "_": " ",
        "/": " ",
        "|": " ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def detect_country_flag(name):
    normalized = normalize_text(name)
    tokens = set(normalized.split())
    for keyword, flag in COUNTRY_FLAGS.items():
        if " " in keyword and keyword in normalized:
            return flag
        if keyword in tokens:
            return flag
    return "🏳️"


def _has_any(text, keywords):
    return any(keyword in text for keyword in keywords)


def is_instagram_link(url):
    try:
        parsed = urlparse(str(url or "").strip())
    except ValueError:
        return False

    if parsed.scheme not in {"http", "https"}:
        return False

    hostname = (parsed.netloc or "").lower()
    if hostname.startswith("www."):
        hostname = hostname[4:]

    return hostname == "instagram.com" or hostname.endswith(".instagram.com")


def classify_smm_service(name, category=""):
    haystack = normalize_text(name, category)

    if not haystack:
        return None

    gift_keywords = ("gift", "heart", "rocket", "diamond", "yurak", "raketa", "olmos")
    bonus_keywords = ("free", "bonus", "tekin")
    telegram_keywords = ("telegram", "tg", "channel", "post", "member", "subscriber")
    instagram_platform_keywords = ("instagram", "insta", "ig")
    instagram_reel_keywords = ("reel", "reels", "view", "views")
    instagram_like_keywords = ("like", "likes", "layk", "layklar", "heart")
    instagram_follower_keywords = (
        "follower",
        "followers",
        "follow",
        "subscriber",
        "subscribers",
        "member",
        "members",
        "obunachi",
        "podpischik",
    )
    uzbek_keywords = ("uzbek", "uzbekistan", "uzb", "ozbek")

    if _has_any(haystack, gift_keywords):
        return _build_group("gift_items")

    if _has_any(haystack, bonus_keywords):
        return _build_group("bonus_free")

    if _has_any(haystack, telegram_keywords):
        if "premium" in haystack:
            return _build_group("tg_premium")
        if _has_any(haystack, uzbek_keywords):
            return _build_group("tg_uzbek")
        if "boost" in haystack or "vote" in haystack:
            return _build_group("tg_boost")
        if "reaction" in haystack or "emoji" in haystack:
            return _build_group("tg_reactions")
        if "view" in haystack or "post" in haystack:
            return _build_group("tg_views")
        return _build_group("tg_premium")

    if _has_any(haystack, instagram_platform_keywords):
        if _has_any(haystack, instagram_follower_keywords):
            return _build_group("ig_followers")
        if _has_any(haystack, instagram_reel_keywords):
            return _build_group("ig_reels")
        if _has_any(haystack, instagram_like_keywords):
            return _build_group("ig_likes")
        return _build_group("ig_followers")

    return None


def _build_group(group_key):
    group_meta = GROUP_META[group_key]
    platform_meta = PLATFORM_META[group_meta["platform_key"]]
    return {
        "platform_key": group_meta["platform_key"],
        "platform_label": platform_meta["label"],
        "platform_emoji": platform_meta["emoji"],
        "platform_sort_order": platform_meta["sort_order"],
        "group_key": group_key,
        "group_label": group_meta["label"],
        "group_emoji": group_meta["emoji"],
        "group_sort_order": group_meta["sort_order"],
        "is_bonus": 1 if group_meta["platform_key"] == "bonus" else 0,
    }


def _to_decimal(value, default="0"):
    try:
        return Decimal(str(value if value is not None else default))
    except (InvalidOperation, ValueError):
        return Decimal(default)


def _to_rate_decimal(value, default="0"):
    try:
        return Decimal(str(float(value if value is not None else default)))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(default)


def _round_uzs(value):
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def apply_markup(rate, markup_percentage):
    rate_decimal = _to_decimal(rate)
    markup_decimal = _to_decimal(markup_percentage)
    return rate_decimal + (rate_decimal * markup_decimal / Decimal("100"))


def calculate_final_price_uzs(provider_price_uzs, usd_rate, markup_percentage, manual_price=None):
    if manual_price is not None:
        return _round_uzs(_to_decimal(manual_price))
    # Current SMM provider returns `rate` already in UZS, so do not multiply by USD rate again.
    base_price_uzs = _to_rate_decimal(provider_price_uzs)
    final_price = apply_markup(base_price_uzs, markup_percentage)
    return _round_uzs(final_price)


def calculate_quantity_price_uzs(price_per_1000, quantity):
    total = (_to_decimal(price_per_1000) * _to_decimal(quantity)) / Decimal("1000")
    return _round_uzs(total)


def calculate_price_uzs(provider_price_uzs, usd_rate, markup_percent, manual_price=None):
    return calculate_final_price_uzs(provider_price_uzs, usd_rate, markup_percent, manual_price)
