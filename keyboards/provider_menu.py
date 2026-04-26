from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def provider_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🚀 Nakrutka"),
        KeyboardButton(text="📱 Raqam olish"),
    )
    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Xizmat turini tanlang...",
    )
