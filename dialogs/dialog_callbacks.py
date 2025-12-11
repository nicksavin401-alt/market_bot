import states as states
import database.requests as database
import dialogs.dialog_getters as dialog_getters
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram.fsm.context import FSMContext
from aiogram_dialog.widgets.kbd import Select

"""Обработчики нажатия кнопок"""


async def category_remove_click(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """Удаление категории после клика на категорию из списка"""
    categories = await database.categories_getter()
    category = None

    for cat in categories:
        if cat.category_id == int(item_id):
            category = cat
            break

    dialog_manager.dialog_data["category_id"] = str(item_id)
    dialog_manager.dialog_data["category_name"] = category.name
    await dialog_manager.next()


async def on_cart_click(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """Открытие корзины"""
    order = await database.cart_order_getter(int(item_id))
    dialog_manager.dialog_data["cart_id"] = int(item_id)
    dialog_manager.dialog_data["cart_name"] = order.product_name
    dialog_manager.dialog_data["cart_quantity"] = order.quantity
    dialog_manager.dialog_data["cart_total_price"] = order.quantity * int(
        order.added_price
    )
    await dialog_manager.next()


async def on_orders_click(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """Открытие заказов"""
    order = await database.order_getter(int(item_id))
    dialog_manager.dialog_data["order_id"] = int(item_id)
    dialog_manager.dialog_data["order_name"] = order.product_name
    dialog_manager.dialog_data["order_quantity"] = order.quantity
    dialog_manager.dialog_data["order_total_price"] = order.quantity * int(
        order.added_price
    )
    await dialog_manager.next()


async def payment_decline(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager
):
    """Отказ от оплаты"""
    order_id = dialog_manager.dialog_data.get("cart_id")
    if await database.remove_cart(order_id):
        await callback.message.edit_text("Заказ успешно удален")
        await dialog_manager.done()


async def order_decline(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager
):
    """Отмена заказа"""
    order_id = dialog_manager.dialog_data.get("order_id")
    if await database.remove_order(order_id):
        await callback.message.edit_text("Заказ успешно отменён")
        await dialog_manager.done()


async def remove_order(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager
):
    """Удаление заказа"""
    order_id = dialog_manager.dialog_data.get("order_id")
    if await database.remove_cart(order_id):
        await callback.message.edit_text("Заказ успешно удален")
        await dialog_manager.done()


async def to_order(callback: CallbackQuery, button, dialog_manager):
    """Обработка кнопки заказать"""
    await dialog_manager.done()
    await callback.message.edit_text("Укажите адрес получения в одном сообщении:")
    fsm: FSMContext = dialog_manager.middleware_data["state"]
    await fsm.set_state(states.Cart.location)


async def on_category_click(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """Открытие категорий в каталоге"""
    categories = await database.categories_getter()
    category = None

    for cat in categories:
        if cat.category_id == int(item_id):
            category = cat
            break

    dialog_manager.dialog_data["category_id"] = str(item_id)
    dialog_manager.dialog_data["category_name"] = category.name
    await dialog_manager.next()


async def on_product_click(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """Открытие продуктов в категории в каталоге"""
    data = await dialog_getters.products_getter(dialog_manager)
    products = data.get("products", [])
    product = None

    for prod in products:
        if prod.product_id == int(item_id):
            product = prod
            break

    await callback.message.edit_text(
        f"Вы выбрали товар: {product.name}"
        f"\nЦена: {product.price} руб."
        "\nВведите количество:"
    )
    await dialog_manager.done()
    fsm: FSMContext = dialog_manager.middleware_data["state"]
    await fsm.update_data(products=item_id)
    await fsm.set_state(states.Catalog.quantity)


async def product_adding(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """Добавление товара после клика на категорию из списка"""

    await callback.message.edit_text("Введите имя нового товара:")
    await dialog_manager.done()
    fsm: FSMContext = dialog_manager.middleware_data["state"]
    await fsm.update_data(choice=item_id)
    await fsm.set_state(states.AddProduct.name)


async def category_remove_click(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """Удаление категории после клика на категорию из списка"""
    categories = await database.categories_getter()
    category = None

    for cat in categories:
        if cat.category_id == int(item_id):
            category = cat
            break

    dialog_manager.dialog_data["category_id"] = str(item_id)
    dialog_manager.dialog_data["category_name"] = category.name
    await dialog_manager.next()


async def category_product_remove_click(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """Выбор категории из которой идет удаление товара после клика на категорию из списка"""
    categories = await database.categories_getter()
    category = None

    for cat in categories:
        if cat.category_id == int(item_id):
            category = cat
            break

    dialog_manager.dialog_data["category_id"] = str(item_id)
    dialog_manager.dialog_data["category_name"] = category.name
    await dialog_manager.next()


async def on_confirm_category_remove(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """Удаление категории выбранной из списка"""
    if await database.remove_category(int(item_id)):
        await callback.message.edit_text("Категория успешно удалена")
        await dialog_manager.done()


async def on_confirm_product_remove(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """Удаление выбранного продукта"""
    if await database.remove_product(int(item_id)):
        await callback.message.edit_text("Товар успешно удален")
        await dialog_manager.done()


async def category_edit_click(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """Ввод нового имени категории после клика на категорию из списка"""
    await callback.message.edit_text("Введите новое имя категории:")
    fsm: FSMContext = dialog_manager.middleware_data["state"]
    await fsm.update_data(editing=int(item_id))
    await fsm.set_state(states.EditCategory.name)
    await dialog_manager.done()


async def product_choice(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """Выбор товара после клика на категорию"""
    categories = await database.categories_getter()
    category = None

    for cat in categories:
        if cat.category_id == int(item_id):
            category = cat
            break

    dialog_manager.dialog_data["category_id"] = str(item_id)
    dialog_manager.dialog_data["category_name"] = category.name
    await dialog_manager.next()


async def edit_product_name(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager
):
    """Ввод нового имени товара после клика на выбор"""
    product_id = dialog_manager.dialog_data.get("product_id")
    await callback.message.edit_text("Введите новое имя товара:")
    fsm: FSMContext = dialog_manager.middleware_data["state"]
    await fsm.update_data(price_or_name=int(product_id))
    await fsm.set_state(states.EditProduct.name)
    await dialog_manager.done()


async def edit_product_price(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager
):
    """Ввод новой цены товара после клика на выбор"""
    product_id = dialog_manager.dialog_data.get("product_id")
    await callback.message.edit_text("Введите новую цену товара:")
    fsm: FSMContext = dialog_manager.middleware_data["state"]
    await fsm.update_data(price_or_name=int(product_id))
    await fsm.set_state(states.EditProduct.price)
    await dialog_manager.done()


async def edit_product_click(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id
):
    """Переход к окну выбора изменений"""
    dialog_manager.dialog_data["product_id"] = int(item_id)
    await dialog_manager.next()
