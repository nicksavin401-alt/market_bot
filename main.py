import logging
import asyncio
import redis.asyncio as aioredis
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.types import BotCommand, BotCommandScopeDefault
from admin_handlers import admin_router
from user_handlers import user_router
from database.models import db_main
from config_reader import config
from dialogs.dialogs import (
    catalog_dialog,
    add_product_dialog,
    remove_category_dialog,
    remove_product_dialog,
    edit_category_dialog,
    edit_product_dialog,
    cart_dialog,
    orders_dialog,
)
from aiogram_dialog import setup_dialogs

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=config.bot_token.get_secret_value(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

redis_ip = config.redis_ip.get_secret_value()


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота 🚀"),
        BotCommand(command="catalog", description="Каталог"),
        BotCommand(command="cart", description="Корзина"),
        BotCommand(command="orders", description="Заказы"),
    ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())


async def main():
<<<<<<< HEAD
    redis = await aioredis.from_url(redis_ip)
=======
    redis = await aioredis.from_url("redis://your.ip")
>>>>>>> 1f6ee0558ad1e9355883a1c9ab26e6368fd99437
    dp = Dispatcher(
        storage=RedisStorage(redis, key_builder=DefaultKeyBuilder(with_destiny=True))
    )
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    dp.include_routers(
        admin_router,
        user_router,
        catalog_dialog,
        add_product_dialog,
        remove_category_dialog,
        remove_product_dialog,
        edit_category_dialog,
        edit_product_dialog,
        cart_dialog,
        orders_dialog,
    )

    setup_dialogs(dp)

    await dp.start_polling(bot)


async def startup(bot: Bot):
    print("\033[31mstarting....\033[0m")
    await set_bot_commands(bot)
    await db_main()


async def shutdown():
    print("\033[31mshutting down....\033[0m")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\033[31merror shutting down!!!!\033[0m")
