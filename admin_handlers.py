from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
import states as states
import keyboards as keyboards
import database.requests as requests
from aiogram.filters import Command, CommandStart
from aiogram_dialog import StartMode, DialogManager
from aiogram.filters import CommandStart

admin_router = Router()

admin_id = 1183927308

@admin_router.message(CommandStart())
async def handle_start(
    message: Message, dialog_manager: DialogManager, state: FSMContext
):
    await state.clear()
    await dialog_manager.reset_stack()
    if await requests.check_admin(message.from_user.id):
        await message.answer(
            "Здравствуйте администратор. Вот список доступных команд:\n"
            "/add_category - Добавить категорию\n"
            "/add_product - Добавить товар\n"
            "/remove_category - Удалить категорию\n"
            "/remove_product -  Удалить товар\n"
            "/edit_category - Редактировать категорию\n"
            "/edit_product -  Редактировать товар\n",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
            "Здравствуйте! Это официальный бот магазина Sartoria. Здесь вы можете заказать товары из нашего каталога. Для этого введите Каталог",
            reply_markup=keyboards.catalog,
        )


"""Добавление категории"""


@admin_router.message(Command("add_category"))
async def create_category(
    message: Message, dialog_manager: DialogManager, state: FSMContext
):
    if await requests.check_admin(message.from_user.id):
        await state.clear()
        await dialog_manager.reset_stack()
        await message.answer(
            "Введите имя новой категории:", reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(states.AddCategory.adding)


@admin_router.message(states.AddCategory.adding)
async def name_category(
    message: Message, dialog_manager: DialogManager, state: FSMContext
):
    if message.text:
        await requests.categories_setter(message.text)
        await message.answer(f"Категория {message.text} добавлена")
        await state.clear()
    else:
        await message.answer("Введите текст!")


"""Удаление категории"""


@admin_router.message(Command("remove_category"))
async def create_category(
    message: Message, dialog_manager: DialogManager, state: FSMContext
):
    if await requests.check_admin(message.from_user.id):
        await state.clear()
        await dialog_manager.start(
            states.RemoveCategory.removing, mode=StartMode.RESET_STACK
        )


"""Добавление товара"""


@admin_router.message(Command("add_product"))
async def create_product(
    message: Message, dialog_manager: DialogManager, state: FSMContext
):
    if await requests.check_admin(message.from_user.id):
        await state.clear()
        await dialog_manager.start(states.AddProduct.choice, mode=StartMode.RESET_STACK)


@admin_router.message(states.AddProduct.name)
async def product_name(
    message: Message, dialog_manager: DialogManager, state: FSMContext
):
    if message.text:
        await state.update_data(name=message.text)
        await state.set_state(states.AddProduct.price)
        await message.answer(f"Введите цену для {message.text}")
    else:
        await message.answer("Введите текст!")


@admin_router.message(states.AddProduct.price)
async def product_price(
    message: Message, dialog_manager: DialogManager, state: FSMContext
):
    if message.text and message.text.isdigit():
        data = await state.get_data()
        price = data["name"]
        category_id = data["choice"]
        await requests.products_setter(price, message.text, category_id)
        await message.answer("Товар добавлен")
        await state.clear()
    else:
        await message.answer("Введите число!")


"""Удаление товара"""


@admin_router.message(Command("remove_product"))
async def create_category(
    message: Message, dialog_manager: DialogManager, state: FSMContext
):
    if await requests.check_admin(message.from_user.id):
        await state.clear()
        await dialog_manager.start(
            states.RemoveProduct.choice_categories, mode=StartMode.RESET_STACK
        )


"""Изменение товара"""


@admin_router.message(Command("edit_product"))
async def create_product(
    message: Message, dialog_manager: DialogManager, state: FSMContext
):
    if await requests.check_admin(message.from_user.id):
        await state.clear()
        await dialog_manager.start(
            states.EditProduct.choice_categories, mode=StartMode.RESET_STACK
        )


@admin_router.message(Command("edit_category"))
async def create_product(
    message: Message, dialog_manager: DialogManager, state: FSMContext
):
    if await requests.check_admin(message.from_user.id):
        await state.clear()
        await dialog_manager.start(states.EditCategory.editing, mode=StartMode.RESET_STACK)


@admin_router.message(states.EditCategory.name)
async def name_category(
    message: Message, dialog_manager: DialogManager, state: FSMContext
):
    if message.text:
        data = await state.get_data()
        category_id = data["editing"]
        if await requests.update_category_name(category_id, message.text):
            await message.answer("Имя категории изменено")
        await state.clear()
    else:
        await message.answer("Введите текст!")


"""Изменение имени товара"""


@admin_router.message(states.EditProduct.name)
async def name_product(
    message: Message, dialog_manager: DialogManager, state: FSMContext
):
    if message.text:
        data = await state.get_data()
        product_id = data["price_or_name"]
        if await requests.update_product(product_id, name = message.text):
            await message.answer("Имя товара изменено")
        await state.clear()
    else:
        await message.answer("Введите текст!")


"""Изменение цены товара"""


@admin_router.message(states.EditProduct.price)
async def price_product(
    message: Message, dialog_manager: DialogManager, state: FSMContext
):
    if message.text and message.text.isdigit():
        data = await state.get_data()
        product_id = data["price_or_name"]
        if await requests.update_product(product_id, price = message.text):
            await message.answer("Цена товара изменена")
        await state.clear()
    else:
        await message.answer("Введите число!")
