from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def profile_inline_keyboard():
    """Shaxsiy kabinet uchun inline tugmalar"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💰 Hisob to'ldirish", callback_data="top_up"),
        InlineKeyboardButton(text="🎁 Chegirma olish", callback_data="get_discount")
    )
    return builder.as_markup()

def referral_inline_keyboard(share_link):
    """Referal tizimi uchun inline tugmalar"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📢 Ulashish", url=f"https://t.me/share/url?url={share_link}&text=SMM va SMS xizmatlari uchun eng yaxshi bot!")
    )
    return builder.as_markup()

def support_inline_keyboard(admin_username):
    """Qo'llab-quvvatlash uchun inline tugmalar"""
    builder = InlineKeyboardBuilder()
    # admin_username can be a link or just the handle
    if admin_username.startswith("http"):
        url = admin_username
    else:
        url = f"https://t.me/{admin_username.replace('@', '')}"
        
    builder.row(
        InlineKeyboardButton(text="👨‍💻 Adminga yozish", url=url)
    )
    return builder.as_markup()
