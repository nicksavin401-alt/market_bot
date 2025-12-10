from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
import states as ST
import keyboards as KB
import database.requests as DB
from aiogram.filters import Command, CommandStart
from aiogram_dialog import StartMode, DialogManager
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config_reader import config

router = Router()

bot = Bot(
    token=config.bot_token.get_secret_value(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
admin_id = int(config.admin_id.get_secret_value())
  
@router.message(CommandStart())
async def handle_start(message: Message, dialog_manager: DialogManager, state: FSMContext):
    await state.clear()
    await dialog_manager.reset_stack() 
    if await DB.check_admin(message.from_user.id):
        await message.answer(
        "Здравствуйте администратор. Вот список доступных команд:\n" \
        "/add_category - Добавить категорию\n" \
        "/add_product - Добавить товар\n" \
        "/remove_category - Удалить категорию\n" \
        "/remove_product -  Удалить товар\n" \
        "/edit_category - Редактировать категорию\n" \
        "/edit_product -  Редактировать товар\n",
        reply_markup=ReplyKeyboardRemove()
    )
    else:
        await message.answer(
        "Здравствуйте! Это официальный бот магазина Sartoria. Здесь вы можете заказать товары из нашего каталога. Для этого введите Каталог",
        reply_markup=KB.catalog
        )

@router.message(F.data == "Каталог")
@router.message(Command("catalog"))
async def handle_catalog(message: Message, dialog_manager: DialogManager, state: FSMContext):
    await state.clear()
    await dialog_manager.start(ST.Catalog.categories, mode=StartMode.RESET_STACK)

@router.message(Command("cart"))
async def handle_catalog(message: Message, dialog_manager: DialogManager, state: FSMContext):
    await state.clear()
    await dialog_manager.start(ST.Cart.products, mode=StartMode.RESET_STACK)

@router.message(Command("orders"))
async def handle_catalog(message: Message, dialog_manager: DialogManager, state: FSMContext):
    await state.clear()
    await dialog_manager.start(ST.Order.products, mode=StartMode.RESET_STACK)

@router.message(ST.Catalog.quantity)
async def product_quantity(message: Message, dialog_manager: DialogManager, state: FSMContext):
    if message.text and message.text.isdigit():
        data = await state.get_data()
        product_id = data["products"]
        await DB.add_to_cart(product_id, message.from_user.id, int(message.text))
        await message.answer("Корзина пополнена!")
        await state.clear()
    else: 
        await message.answer("Введите текст!")

"""Оплата"""

@router.callback_query(F.data == "change_address")
async def change_address_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Укажите адрес получения в одном сообщении:")
    await state.set_state(ST.Cart.location)


@router.message(ST.Cart.location)
async def order_location(message: Message, dialog_manager: DialogManager, state: FSMContext):
    if message.text:
        address = message.text
        
        await state.update_data({'delivery_address': address})
        
        await message.answer(
            f"📦 <b>Адрес доставки:</b>\n"
            f"{address}\n\n"
            f"Подтвердить адрес?",
            parse_mode='HTML',
            reply_markup=KB.location_keyboard
        )

    else:
        await message.answer(
            "Пожалуйста, введите адрес текстом"
        )
    

@router.callback_query(F.data == "confirm_address")
async def confirm_address_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    address = data.get('delivery_address', 'Адрес не указан')

    total_amount = await DB.getter_cart_amount(callback.from_user.id)
    await callback.message.edit_text(f"✅ <b>Адрес подтвержден!</b>\n"
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
                                     reply_markup= KB.confirm_payment_keyboard)

    user = callback.from_user
    await state.update_data({'user_id': user.id,
                             'first_name': user.first_name})

@router.callback_query(F.data == "confirm_payment")
async def confirm_payment_handler(callback: CallbackQuery, state: FSMContext):
    if not DB.order_getter(id):
        await bot.send_message(admin_id, f"Подтвердите оплату пользователя {callback.from_user.id}", reply_markup = KB.admin_keyboard)
        await callback.message.answer("Ожидаем подтверждение оплаты администратором...")

@router.callback_query(F.data.startswith("admin_confirm"))
async def handle_address_action(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('user_id')
    first_name = data.get('first_name')
    await callback.message.answer(f"Подтверждена оплата для {first_name}")
    if DB.transfer_cart_to_orders(user_id):
        await bot.send_message(user_id, "Оплата подтверждена успешно! Благодарим за заказ")
    

@router.callback_query(F.data.startswith("admin_reject"))
async def handle_address_action(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('user_id')
    await callback.message.answer(f"Отклонена оплата для {user_id}")
    await bot.send_message(user_id, "Оплата не прошла, пожалуйста, проверьте платёж :C")

"""Добавление категории"""

@router.message(Command("add_category"))
async def create_category(message: Message, dialog_manager: DialogManager, state: FSMContext):
    await state.clear()
    await dialog_manager.reset_stack() 
    await message.answer("Введите имя новой категории:",reply_markup=ReplyKeyboardRemove())
    await state.set_state(ST.AddCategory.adding)
  
@router.message(ST.AddCategory.adding)
async def name_category(message: Message, dialog_manager: DialogManager, state: FSMContext):
    if message.text:
        await DB.categories_setter(message.text)
        await message.answer(f"Категория {message.text} добавлена")
        await state.clear()
    else: 
        await message.answer("Введите текст!")

"""Удаление категории"""

@router.message(Command("remove_category"))
async def create_category(message: Message, dialog_manager: DialogManager, state: FSMContext):
    await state.clear()
    await dialog_manager.start(ST.RemoveCategory.removing, mode=StartMode.RESET_STACK)

"""Добавление товара"""

@router.message(Command("add_product"))
async def create_product(message: Message, dialog_manager: DialogManager, state: FSMContext):
    await state.clear()
    await dialog_manager.start(ST.AddProduct.choice, mode=StartMode.RESET_STACK)

@router.message(ST.AddProduct.name)
async def product_name(message: Message, dialog_manager: DialogManager, state: FSMContext):
    if message.text:
        await state.update_data(name=message.text)        
        await state.set_state(ST.AddProduct.price)
        await message.answer(f"Введите цену для {message.text}") 
    else: 
        await message.answer("Введите текст!")

@router.message(ST.AddProduct.price)
async def product_price(message: Message, dialog_manager: DialogManager, state: FSMContext):
    if message.text and message.text.isdigit():
        data = await state.get_data()
        price = data["name"]
        category_id = data["choice"]
        print(message.text, price, category_id)
        await DB.products_setter(price, message.text, category_id)
        await message.answer("Товар добавлен")
        await state.clear()
    else: 
        await message.answer("Введите число!")

"""Удаление товара"""

@router.message(Command("remove_product"))
async def create_category(message: Message, dialog_manager: DialogManager, state: FSMContext):
    await state.clear()
    await dialog_manager.start(ST.RemoveProduct.choice_categories, mode=StartMode.RESET_STACK)

"""Изменение товара"""

@router.message(Command("edit_product"))
async def create_product(message: Message, dialog_manager: DialogManager, state: FSMContext):
    await state.clear()
    await dialog_manager.start(ST.EditProduct.choice_categories, mode=StartMode.RESET_STACK)

@router.message(Command("edit_category"))
async def create_product(message: Message, dialog_manager: DialogManager, state: FSMContext):
    await state.clear()
    await dialog_manager.start(ST.EditCategory.editing, mode=StartMode.RESET_STACK)

@router.message(ST.EditCategory.name)
async def name_category(message: Message, dialog_manager: DialogManager, state: FSMContext):
    if message.text:
        data = await state.get_data()
        category_id = data['editing']
        if await DB.update_category_name(category_id, message.text):
            await message.answer("Имя категории изменено")
        await state.clear()
    else: 
        await message.answer("Введите текст!")

"""Изменение имени товара"""

@router.message(ST.EditProduct.name)
async def name_product(message: Message, dialog_manager: DialogManager, state: FSMContext):
    if message.text:
        data = await state.get_data()
        product_id = data['price_or_name']
        if await DB.update_product_name(product_id, message.text):
            await message.answer("Имя товара изменено")
        await state.clear()
    else: 
        await message.answer("Введите текст!")

"""Изменение цены товара"""

@router.message(ST.EditProduct.price)
async def price_product(message: Message, dialog_manager: DialogManager, state: FSMContext):
    if message.text and message.text.isdigit():
        data = await state.get_data()
        product_id = data['price_or_name']
        if await DB.update_product_price(product_id, message.text):
            await message.answer("Цена товара изменена")
        await state.clear()
    else: 
        await message.answer("Введите число!")