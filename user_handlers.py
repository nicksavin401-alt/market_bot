from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import states as states
import keyboards as keyboards
import database.requests as requests
from aiogram.filters import Command, StateFilter
from aiogram_dialog import StartMode, DialogManager
from config_reader import config

user_router = Router()

admin_id = int(config.admin_id.get_secret_value())


@user_router.message(F.data == "Каталог")
@user_router.message(Command("catalog"))
async def handle_catalog(
    message: Message, dialog_manager: DialogManager, state: FSMContext
):
    await state.clear()
    await dialog_manager.start(states.Catalog.categories, mode=StartMode.RESET_STACK)


@user_router.message(Command("cart"))
async def handle_catalog(
    message: Message, dialog_manager: DialogManager, state: FSMContext
):
    await state.clear()
    await dialog_manager.start(states.Cart.products, mode=StartMode.RESET_STACK)


@user_router.message(Command("orders"))
async def handle_catalog(
    message: Message, dialog_manager: DialogManager, state: FSMContext
):
    await state.clear()
    await dialog_manager.start(states.Order.products, mode=StartMode.RESET_STACK)


@user_router.message(states.Catalog.quantity)
async def product_quantity(
    message: Message, dialog_manager: DialogManager, state: FSMContext
):
    if message.text and message.text.isdigit():
        data = await state.get_data()
        product_id = data["products"]
        await requests.add_to_cart(product_id, message.from_user.id, int(message.text))
        await message.answer("Корзина пополнена!")
        await state.clear()
    else:
        await message.answer("Введите текст!")


"""Оплата"""


@user_router.callback_query(F.data == "change_address")
async def change_address_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Укажите адрес получения в одном сообщении:")
    await state.set_state(states.Cart.location)


@user_router.message(states.Cart.location)
async def order_location(
    message: Message, dialog_manager: DialogManager, state: FSMContext
):
    if message.text:
        address = message.text

        await state.update_data({"delivery_address": address})

        await message.answer(
            f"📦 <b>Адрес доставки:</b>\n" f"{address}\n\n" f"Подтвердить адрес?",
            parse_mode="HTML",
            reply_markup=keyboards.location_keyboard,
        )

    else:
        await message.answer("Пожалуйста, введите адрес текстом")


@user_router.callback_query(F.data == "confirm_address")
async def confirm_address_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    address = data.get("delivery_address", "Адрес не указан")
    total_amount = await requests.getter_cart_amount(callback.from_user.id)
    await callback.message.edit_text(
        f"✅ <b>Адрес подтвержден!</b>\n"
        f"📍 <b>Адрес доставки:</b>\n"
        f"{address}\n\n"
        f"💰 <b>Сумма к оплате:</b> {total_amount} ₽\n\n"
        f"💳 <b>Оплатите заказ по реквизитам:</b>\n"
        f"<code>2200 1234 5678 9012</code>\n"
        f"Тинькофф / Иван И.\n\n"
        f"📱 <b>Или через СБП по номеру:</b>\n"
        f"<code>+7 (999) 123-45-67</code>\n\n"
        f"<i>В комментарии к платежу укажите:</i>\n"
        f"<code>Заказ от {callback.from_user.first_name}</code>\n\n"
        f"После оплаты нажмите кнопку ниже ⬇️",
        reply_markup=keyboards.confirm_payment_keyboard,
    )


@user_router.callback_query(F.data == "confirm_payment", StateFilter(states.Cart.location))
async def confirm_payment_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    total_amount = await requests.getter_cart_amount(callback.from_user.id)
    data = await state.get_data()
    address = data.get("delivery_address", "Адрес не указан")
    await bot.send_message(
        admin_id,
        f"Подтвердите оплату пользователя {callback.from_user.first_name}",
        reply_markup=keyboards.admin_keyboard(callback.from_user.id),
    )
    await callback.message.answer("Ожидаем подтверждение оплаты администратором...")
    await callback.message.edit_text(
        f"✅ <b>Адрес подтвержден!</b>\n"
        f"📍 <b>Адрес доставки:</b>\n"
        f"{address}\n\n"
        f"💰 <b>Сумма к оплате:</b> {total_amount} ₽\n\n"
        f"💳 <b>Оплатите заказ по реквизитам:</b>\n"
        f"<code>2200 1234 5678 9012</code>\n"
        f"Тинькофф / Иван И.\n\n"
        f"📱 <b>Или через СБП по номеру:</b>\n"
        f"<code>+7 (999) 123-45-67</code>\n\n"
        f"<i>В комментарии к платежу укажите:</i>\n"
        f"<code>Заказ от {callback.from_user.first_name}</code>",
        reply_markup=None,
    )


@user_router.callback_query(F.data.startswith("admin_confirm"))
async def handle_address_action(callback: CallbackQuery, state: FSMContext, bot: Bot):

    user_id = int(callback.data.split("/")[1])
    user = await bot.get_chat(user_id)
    first_name = user.first_name
    await callback.message.edit_text(
        f"Подтверждена оплата для {first_name}", reply_markup=None
    )
    if await requests.transfer_cart_to_orders(user_id):
        await bot.send_message(
            user_id, "Оплата подтверждена успешно! Благодарим за заказ"
        )
    else:
        await callback.message.edit_text(
            f"Не прошла оплата для {first_name}", reply_markup=None
        )


@user_router.callback_query(F.data.startswith("admin_reject"))
async def handle_address_action(callback: CallbackQuery, state: FSMContext, bot: Bot):
    user_id = int(callback.data.split("/")[1])
    user = await bot.get_chat(user_id)
    first_name = user.first_name
    await callback.message.edit_text(
        f"Отклонена оплата для {first_name}", reply_markup=None
    )
    await bot.send_message(user_id, "Оплата не прошла, пожалуйста, проверьте платёж :C")
