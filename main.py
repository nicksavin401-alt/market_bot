import logging
import asyncio
import redis.asyncio as aioredis
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.types import BotCommand, BotCommandScopeDefault
from handlers import router
from database.models import async_main
from config_reader import config
from dialogs import( 
    catalog_dialog, 
    add_product_dialog,
    remove_category_dialog,
    remove_product_dialog,
    edit_category_dialog,
    edit_product_dialog,
    cart_dialog,
    orders_dialog
)
from aiogram_dialog import setup_dialogs

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=config.bot_token.get_secret_value(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота 🚀"),
        BotCommand(command="catalog", description="Каталог"),
        BotCommand(command="cart", description="Корзина"),
        BotCommand(command="orders", description="Заказы")
    ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())


async def main():
    redis = await aioredis.from_url("redis://your.ip")
    dp = Dispatcher(
        storage=RedisStorage(redis, key_builder=DefaultKeyBuilder(with_destiny=True))
    )
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    dp.include_routers(
        router, 
        catalog_dialog, 
        add_product_dialog,
        remove_category_dialog,
        remove_product_dialog,
        edit_category_dialog,
        edit_product_dialog,
        cart_dialog,
        orders_dialog
    )

    setup_dialogs(dp)

    await dp.start_polling(bot)


async def startup(bot: Bot):
    print("\033[31mstarting....\033[0m")
    await set_bot_commands(bot)
    await async_main()


async def shutdown():
    print("\033[31mshutting down....\033[0m")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("error shutting down!!!!")
