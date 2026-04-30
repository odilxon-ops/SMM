import asyncio
import logging

import runtime_bootstrap
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import ADMINS, BOT_TOKEN, validate_runtime_config
from database.models import init_db
from handlers import (
    order_handlers,
    payment_handlers,
    provider_structure_handlers,
    referral,
    services_handlers,
    smm_handlers,
    sms_handlers,
    start_handlers,
    user_handlers,
)
from handlers.admin import admin_router
from middlewares.check_status import CheckStatusMiddleware
from middlewares.throttling import ThrottlingMiddleware
from utils.order_sync import sync_smm_orders


async def on_startup(bot: Bot):
    await init_db()

    for admin_id in ADMINS:
        try:
            await bot.send_message(admin_id, "🚀 <b>Bot muvaffaqiyatli ishga tushdi!</b>")
        except Exception as exc:
            logging.error("Admin %s ga xabar yuborib bo'lmadi: %s", admin_id, exc)


async def main():
    config_errors = validate_runtime_config()
    if config_errors:
        raise RuntimeError("Config xatolari: " + "; ".join(config_errors))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start_handlers.router)
    dp.include_router(user_handlers.router)
    dp.include_router(referral.router)
    dp.include_router(provider_structure_handlers.router)
    dp.include_router(services_handlers.router)
    dp.include_router(smm_handlers.router)
    dp.include_router(sms_handlers.router)
    dp.include_router(payment_handlers.router)
    dp.include_router(admin_router)
    dp.include_router(order_handlers.router)

    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())
    dp.message.middleware(CheckStatusMiddleware())
    dp.callback_query.middleware(CheckStatusMiddleware())
    dp.startup.register(on_startup)

    asyncio.create_task(sync_smm_orders())
    
    try:
        while True:
            try:
                print("Bot ishga tushdi...")
                await dp.start_polling(bot)
            except Exception as e:
                logging.error(f"Polling xatosi: {e}")
                await asyncio.sleep(5)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi")
