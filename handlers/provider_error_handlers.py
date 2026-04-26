import logging

from aiogram import types

from providers.exceptions import (
    ProviderAuthError,
    ProviderError,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)

logger = logging.getLogger(__name__)


async def _reply(target: types.Message | types.CallbackQuery, text: str):
    if isinstance(target, types.CallbackQuery):
        await target.message.answer(text)
        await target.answer()
    else:
        await target.answer(text)


async def handle_smm_provider_error(target: types.Message | types.CallbackQuery, error: Exception):
    logger.exception("SMM provider error", exc_info=error)
    if isinstance(error, ProviderAuthError):
        return await _reply(target, "❌ Nakrutka API kaliti noto'g'ri yoki muddati tugagan.")
    if isinstance(error, ProviderTimeoutError):
        return await _reply(target, "⏳ Nakrutka API javob bermayapti. Keyinroq urinib ko'ring.")
    if isinstance(error, ProviderUnavailableError):
        return await _reply(target, "⚠️ Nakrutka API vaqtincha ishlamayapti.")
    if isinstance(error, ProviderResponseError):
        return await _reply(target, "⚠️ Nakrutka API noto'g'ri javob qaytardi.")
    if isinstance(error, ProviderError):
        return await _reply(target, "❌ Nakrutka bo'limida kutilmagan xatolik yuz berdi.")
    return await _reply(target, "❌ Nakrutka so'rovi bajarilmadi.")


async def handle_sms_provider_error(target: types.Message | types.CallbackQuery, error: Exception):
    logger.exception("SMS provider error", exc_info=error)
    if isinstance(error, ProviderAuthError):
        return await _reply(target, "❌ SMS API kaliti noto'g'ri yoki bloklangan.")
    if isinstance(error, ProviderTimeoutError):
        return await _reply(target, "⏳ SMS API javob bermayapti. Keyinroq qayta urinib ko'ring.")
    if isinstance(error, ProviderUnavailableError):
        return await _reply(target, "⚠️ SMS API vaqtincha ishlamayapti.")
    if isinstance(error, ProviderResponseError):
        return await _reply(target, "⚠️ SMS API noto'g'ri yoki bo'sh javob qaytardi.")
    if isinstance(error, ProviderError):
        return await _reply(target, "❌ Raqam olish bo'limida kutilmagan xatolik yuz berdi.")
    return await _reply(target, "❌ SMS so'rovi bajarilmadi.")
