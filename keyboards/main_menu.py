from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_menu_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📞 Raqam olish"),
        KeyboardButton(text="⚡️ Tezkor Nakrutka"),
    )
    builder.row(
        KeyboardButton(text="💰 Hisob to'ldirish"),
        KeyboardButton(text="📊 Buyurtmalarim"),
    )
    builder.row(
        KeyboardButton(text="💰 Pul ishlash"),
        KeyboardButton(text="💎 Bonuslar"),
    )
    builder.row(
        KeyboardButton(text="🖥 Akkaunt"),
    )
    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Kerakli bo'limni tanlang...",
    )
