from html import escape

from aiogram import Bot, types
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import REFERRAL_BONUS
from database.models import db


async def get_referral_bonus_amount() -> int:
    raw_value = await db.get_setting("referral_bonus", str(REFERRAL_BONUS))
    try:
        bonus = int(float(raw_value))
    except (TypeError, ValueError):
        bonus = int(REFERRAL_BONUS)
    return max(0, bonus)


async def build_referral_link(bot: Bot, user_id: int) -> str:
    me = await bot.get_me()
    username = (me.username or "").strip()
    if not username:
        return f"https://t.me/?start={int(user_id)}"
    return f"https://t.me/{username}?start={int(user_id)}"


def referral_share_keyboard(referral_link: str):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="🔗 Taklif qilish",
            switch_inline_query=f"referral:{referral_link}",
        )
    )
    return builder.as_markup()


async def process_referral_reward(bot: Bot, order) -> str:
    if not order or str(order["status"]) != "completed":
        return "ignored"

    reward_info, status = await db.award_referral_bonus_for_completed_order(order["user_id"], order["id"])
    if status == "rewarded":
        reward_amount = int(reward_info["reward_amount"])
        try:
            await bot.send_message(
                reward_info["inviter_user_id"],
                "🎉 Tabriklaymiz! "
                f"Do'stingiz buyurtma berdi va hisobingizga <b>{reward_amount:,.0f}</b> so'm qo'shildi.",
            )
        except (TelegramBadRequest, TelegramForbiddenError):
            pass
    elif status == "already_rewarded" and reward_info:
        try:
            await bot.send_message(
                reward_info["inviter_user_id"],
                "ℹ️ Siz bu foydalanuvchi orqali avval pul olgansiz.",
            )
        except (TelegramBadRequest, TelegramForbiddenError):
            pass
    return status


async def build_referral_message(bot: Bot, user_id: int) -> tuple[str, types.InlineKeyboardMarkup]:
    referral_link = await build_referral_link(bot, user_id)
    bonus = await get_referral_bonus_amount()
    invited_count = await db.get_referral_stats(user_id)
    rewarded_count = await db.get_referral_reward_count(user_id)

    text = (
        "🎁 Do'stlaringizni taklif qiling va pul ishlang!\n\n"
        f"1 ta odam -> {bonus:,.0f} so'm\n"
        f"10 ta odam -> {bonus * 10:,.0f} so'm\n"
        f"100 ta odam -> {bonus * 100:,.0f} so'm\n\n"
        "⚠️ Pul berilishi uchun do'stingiz kamida 1 ta buyurtma berishi shart!\n\n"
        f"👥 Taklif qilganlar: <b>{invited_count}</b>\n"
        f"✅ Bonus olinganlar: <b>{rewarded_count}</b>\n\n"
        f"🔗 Havolangiz:\n<code>{escape(referral_link)}</code>"
    )
    return text, referral_share_keyboard(referral_link)
