import asyncio
import logging

import runtime_bootstrap
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, ADMINS, validate_runtime_config
from database.models import init_db
from handlers import (
    admin_handlers,
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
from aiogram.client.default import DefaultBotProperties
from middlewares.check_status import CheckStatusMiddleware

async def on_startup(bot: Bot):
    """Bot ishga tushganda bajariladigan amallar"""
    # Bazani yaratish
    await init_db()
    
    # Adminlarga xabar yuborish
    for admin_id in ADMINS:
        try:
            await bot.send_message(admin_id, "🚀 <b>Bot muvaffaqiyatli ishga tushdi!</b>")
        except Exception as e:
            logging.error(f"Admin {admin_id} ga xabar yuborib bo'lmadi: {e}")

async def main():
    config_errors = validate_runtime_config()
    if config_errors:
        raise RuntimeError("Config xatolari: " + "; ".join(config_errors))

    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    
    # Bot va Dispatcher
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=MemoryStorage())
    
    # Routerlarni ulash
    dp.include_router(start_handlers.router)
    dp.include_router(user_handlers.router)
    dp.include_router(referral.router)
    dp.include_router(provider_structure_handlers.router)
    dp.include_router(services_handlers.router)
    dp.include_router(smm_handlers.router)
    dp.include_router(sms_handlers.router)
    dp.include_router(payment_handlers.router)
    dp.include_router(admin_handlers.router)
    dp.include_router(order_handlers.router)
    
    # Middlewarelarni ro'yxatdan o'tkazish
    dp.message.middleware(CheckStatusMiddleware())
    dp.callback_query.middleware(CheckStatusMiddleware())
    
    # Startup funksiyasini ro'yxatdan o'tkazish
    dp.startup.register(on_startup)
    
    # Polling boshlash
    try:
        print("Bot ishga tushdi...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi")
