from aiogram import F, Router, types
from aiogram.filters import Command

from config import POSTGRES_DSN, SMM_API_KEY, SMM_API_URL, SMS_API_KEY, SMS_API_URL
from handlers.provider_error_handlers import (
    handle_smm_provider_error,
    handle_sms_provider_error,
)
from keyboards.provider_menu import provider_main_menu
from providers.smm_provider import SMMProvider
from providers.sms_provider import SMSProvider
from repositories.postgres import PostgresRepository
from services.balance_service import UnifiedBalanceService

router = Router()

postgres_repo = PostgresRepository(POSTGRES_DSN)
balance_service = UnifiedBalanceService(postgres_repo)
smm_provider = SMMProvider(SMM_API_KEY, SMM_API_URL)
sms_provider = SMSProvider(SMS_API_KEY, SMS_API_URL)


def _user_identity(message: types.Message) -> tuple[int, str | None, str | None]:
    user = message.from_user
    return user.id, user.username, user.full_name


@router.message(Command("provider_start"))
async def provider_start(message: types.Message):
    try:
        user_id, username, full_name = _user_identity(message)
        await balance_service.bootstrap_user(user_id, username, full_name)
        balance = await balance_service.get_balance(user_id)
    except Exception as error:
        return await message.answer(f"❌ PostgreSQL ulanishi tayyor emas: {error}")

    await message.answer(
        "Ikki provayderli demo menyu tayyor.\n\n"
        f"Umumiy balans: <b>{balance:,}</b> so'm\n"
        "Quyidagi bo'limlardan birini tanlang:",
        reply_markup=provider_main_menu(),
    )


@router.message(F.text == "🚀 Nakrutka")
async def provider_smm_menu(message: types.Message):
    user_id, username, full_name = _user_identity(message)
    try:
        await balance_service.bootstrap_user(user_id, username, full_name)
        balance = await balance_service.get_balance(user_id)
    except Exception as error:
        return await message.answer(f"❌ PostgreSQL xatoligi: {error}")

    try:
        services = await smm_provider.get_services()
    except Exception as error:
        return await handle_smm_provider_error(message, error)

    preview = []
    for service in services[:10]:
        name = str(service.get("name", "Noma'lum xizmat"))
        rate = str(service.get("rate", "0"))
        preview.append(f"• {name} - ${rate}/1000")

    await message.answer(
        "🚀 <b>Nakrutka bo'limi</b>\n\n"
        f"Balans: <b>{balance:,}</b> so'm\n"
        f"Topilgan xizmatlar: <b>{len(services)}</b>\n\n"
        + "\n".join(preview or ["Xizmat topilmadi."]),
        reply_markup=provider_main_menu(),
    )


@router.message(F.text == "📱 Raqam olish")
async def provider_sms_menu(message: types.Message):
    user_id, username, full_name = _user_identity(message)
    try:
        await balance_service.bootstrap_user(user_id, username, full_name)
        balance = await balance_service.get_balance(user_id)
    except Exception as error:
        return await message.answer(f"❌ PostgreSQL xatoligi: {error}")

    try:
        countries = await sms_provider.get_countries()
    except Exception as error:
        return await handle_sms_provider_error(message, error)

    preview = []
    for country_id, info in list(countries.items())[:10]:
        name = str(info.get("name", country_id))
        count = int(info.get("count", 0) or 0)
        price = info.get("price", "0")
        preview.append(f"• {name} - {count} ta - {price}")

    await message.answer(
        "📱 <b>Raqam olish bo'limi</b>\n\n"
        f"Balans: <b>{balance:,}</b> so'm\n"
        f"Davlatlar soni: <b>{len(countries)}</b>\n\n"
        + "\n".join(preview or ["Davlatlar topilmadi."]),
        reply_markup=provider_main_menu(),
    )
