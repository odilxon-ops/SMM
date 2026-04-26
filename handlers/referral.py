from hashlib import md5

from aiogram import Bot, F, Router, types

from services.referral_service import build_referral_link, build_referral_message

router = Router()


@router.message(F.text == "💰 Pul ishlash")
async def referral_menu_handler(message: types.Message, bot: Bot):
    text, keyboard = await build_referral_message(bot, message.from_user.id)
    await message.answer(text, reply_markup=keyboard)


@router.inline_query(F.query.startswith("referral:"))
async def referral_inline_query_handler(inline_query: types.InlineQuery, bot: Bot):
    referral_link = inline_query.query.split("referral:", 1)[1].strip()
    if not referral_link.startswith("https://t.me/"):
        referral_link = await build_referral_link(bot, inline_query.from_user.id)

    article = types.InlineQueryResultArticle(
        id=md5(referral_link.encode("utf-8")).hexdigest(),
        title="🔗 Referal havolani yuborish",
        description="Do'stingizga bot havolasini yuboring",
        input_message_content=types.InputTextMessageContent(
            message_text=(
                "🎁 SMM botga qo'shiling va bonus oling!\n\n"
                f"{referral_link}\n\n"
                "⚠️ Bonus olish uchun birinchi buyurtmani berish kerak."
            )
        ),
    )
    await inline_query.answer([article], cache_time=0, is_personal=True)
