from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def user_home_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🏠 Asosiy sahifa", callback_data="user_main"))
    return builder.as_markup()


def user_flow_keyboard(
    *,
    back_callback=None,
    back_text="🔙 Orqaga",
    include_home=True,
    include_cancel=False,
):
    builder = InlineKeyboardBuilder()

    if back_callback:
        builder.row(types.InlineKeyboardButton(text=back_text, callback_data=back_callback))

    action_buttons = []
    if include_home:
        action_buttons.append(types.InlineKeyboardButton(text="🏠 Asosiy sahifa", callback_data="user_main"))
    if include_cancel:
        action_buttons.append(types.InlineKeyboardButton(text="❌ Bekor qilish", callback_data="user_cancel"))

    if action_buttons:
        builder.row(*action_buttons)

    return builder.as_markup()
