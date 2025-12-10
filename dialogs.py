import states as ST
import keyboards as KB
import database.requests as DB
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Button, Row
from aiogram_dialog.widgets.text import Format, Const
from dataclasses import dataclass
from aiogram.types import CallbackQuery

@dataclass
class Category:
    id: int
    name: str

@dataclass
class Product:
    id: int
    name: str
    price: float

async def categories_getter(dialog_manager: DialogManager, **kwargs):
    categories = await DB.categories_getter()
    return {
        "categories": categories,
        "exists": bool(categories)
    }

async def products_getter(dialog_manager: DialogManager, **kwargs):
    # Получаем ID выбранной категории из dialog_data
    category_id = dialog_manager.dialog_data.get('category_id')
    category_name = dialog_manager.dialog_data.get("category_name")
    
    # База данных товаров по категориям
    all_products = await DB.products_getter()
    
    products = []
    for p in all_products:  
        if p.category_id == int(category_id):
            products.append(p)

    return {
        "products": products,
        "exists": bool(products),
        "category_id": category_id,
        "category_name": category_name
    }

async def cart_getter(dialog_manager: DialogManager, **kwargs):
    
    user_id = dialog_manager.event.from_user.id
    # База данных товаров по id
    products = await DB.cart_getter(user_id)
    cart_price = 0

    for product in products:
        product.total_price = product.quantity * int(product.added_price)
        cart_price += product.total_price
    
    return {
        "products": products,
        "exists": bool(products),
        "cart_price": cart_price
    }

async def dialog_data_getter(dialog_manager: DialogManager, **kwargs):
    return dialog_manager.dialog_data

"""Обработчики нажатия кнопок"""

async def category_remove_click(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    """Удаление категории после клика на категорию из списка"""
    categories = await DB.categories_getter()
    category = None
 
    for cat in categories:
        if cat.category_id == int(item_id):
            category = cat
            break

    dialog_manager.dialog_data["category_id"] = str(item_id)
    dialog_manager.dialog_data["category_name"] = category.name
    await dialog_manager.next()

async def on_cart_click(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    """Открытие корзины"""
    order = await DB.cart_order_getter(int(item_id))
    dialog_manager.dialog_data["order_id"] = int(item_id)
    dialog_manager.dialog_data["order_name"] = order.product_name
    dialog_manager.dialog_data["order_quantity"] = order.quantity
    dialog_manager.dialog_data["order_total_price"] = order.quantity * int(order.added_price)
    await dialog_manager.next()

async def on_orders_click(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    """Открытие заказа"""
    order = await DB.order_getter(int(item_id))
    dialog_manager.dialog_data["order_id"] = int(item_id)
    dialog_manager.dialog_data["order_name"] = order.product_name
    dialog_manager.dialog_data["order_quantity"] = order.quantity
    dialog_manager.dialog_data["order_total_price"] = order.quantity * int(order.added_price)
    await dialog_manager.next()

async def payment_decline(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager):
    """Отказ от заказа"""
    order_id = dialog_manager.dialog_data.get('order_id')
    if await DB.remove_cart(order_id):
        await callback.message.edit_text(
            "Заказ успешно удален"
        )
        await dialog_manager.done()

async def remove_order(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager):
    """Удаление заказа"""
    order_id = dialog_manager.dialog_data.get('order_id')
    if await DB.remove_cart(order_id):
        await callback.message.edit_text(
            "Заказ успешно удален"
        )
        await dialog_manager.done()

async def to_order(callback: CallbackQuery, button, dialog_manager):
    '''Обработка кнопки заказать'''
    await dialog_manager.done()
    await callback.message.edit_text("Укажите адрес получения в одном сообщении:")
    fsm: FSMContext = dialog_manager.middleware_data["state"]
    await fsm.set_state(ST.Cart.location)

async def go_back(callback, button, dialog_manager):
    '''Обработка кнопки назад'''
    await dialog_manager.back()

async def on_category_click(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    """Открытие категорий в каталоге"""
    categories = await DB.categories_getter()
    category = None

    for cat in categories:
        if cat.category_id == int(item_id):
            category = cat
            break 

    dialog_manager.dialog_data["category_id"] = str(item_id)
    dialog_manager.dialog_data["category_name"] = category.name
    await dialog_manager.next()


async def on_product_click(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    """Открытие продуктов в категории в каталоге"""
    data = await products_getter(dialog_manager)
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
    await fsm.set_state(ST.Catalog.quantity)

async def product_adding(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    """Добавление товара после клика на категорию из списка"""

    await callback.message.edit_text("Введите имя нового товара:")
    await dialog_manager.done()
    fsm: FSMContext = dialog_manager.middleware_data["state"]
    await fsm.update_data(choice=item_id)    
    await fsm.set_state(ST.AddProduct.name)

async def category_remove_click(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    """Удаление категории после клика на категорию из списка"""
    categories = await DB.categories_getter()
    category = None
 
    for cat in categories:
        if cat.category_id == int(item_id):
            category = cat
            break

    dialog_manager.dialog_data["category_id"] = str(item_id)
    dialog_manager.dialog_data["category_name"] = category.name
    await dialog_manager.next()

async def category_product_remove_click(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    """Выбор категории из которой идет удаление товара после клика на категорию из списка"""
    categories = await DB.categories_getter()
    category = None

    for cat in categories:
        if cat.category_id == int(item_id):
            category = cat
            break

    dialog_manager.dialog_data["category_id"] = str(item_id)
    dialog_manager.dialog_data["category_name"] = category.name
    await dialog_manager.next()

async def on_confirm_category_remove(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    """Удаление категории выбранной из списка"""
    if await DB.remove_category(int(item_id)):
        await callback.message.edit_text(
            "Категория успешно удалена"
        )
        await dialog_manager.done()

async def on_confirm_product_remove(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    """Удаление выбранного продукта"""
    if await DB.remove_product(int(item_id)):
        await callback.message.edit_text(
            "Товар успешно удален"
        )
        await dialog_manager.done()

async def category_edit_click(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    """Ввод нового имени категории после клика на категорию из списка"""
    await callback.message.edit_text("Введите новое имя категории:")
    fsm: FSMContext = dialog_manager.middleware_data["state"]
    await fsm.update_data(editing=int(item_id))    
    await fsm.set_state(ST.EditCategory.name)
    await dialog_manager.done()

async def product_choice(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    """Выбор товара после клика на категорию"""
    categories = await DB.categories_getter()
    category = None

    for cat in categories:
        if cat.category_id == int(item_id):
            category = cat
            break

    dialog_manager.dialog_data["category_id"] = str(item_id)
    dialog_manager.dialog_data["category_name"] = category.name
    await dialog_manager.next()

async def edit_product_name(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager):
    """Ввод нового имени товара после клика на выбор"""
    product_id = dialog_manager.dialog_data.get('product_id')
    await callback.message.edit_text("Введите новое имя товара:")
    fsm: FSMContext = dialog_manager.middleware_data["state"]
    await fsm.update_data(price_or_name=int(product_id))    
    await fsm.set_state(ST.EditProduct.name)
    await dialog_manager.done()

async def edit_product_price(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager):
    """Ввод новой цены товара после клика на выбор"""
    product_id = dialog_manager.dialog_data.get('product_id')
    await callback.message.edit_text("Введите новую цену товара:")
    fsm: FSMContext = dialog_manager.middleware_data["state"]
    await fsm.update_data(price_or_name=int(product_id))    
    await fsm.set_state(ST.EditProduct.price)
    await dialog_manager.done()

async def edit_product_click(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id):
    """Переход к окну выбора изменений"""
    dialog_manager.dialog_data["product_id"] = int(item_id)
    await dialog_manager.next()

"""Окна"""

decline_order = Window(
    Format("Отменить заказ?"),
    Row(
        Button(Const("Отменить"), id="decline", on_click=payment_decline)
    ),
    Button(
        Const("⬅ Назад"),
        id="go_back",
        on_click=go_back
    ),
    getter=dialog_data_getter,
    state=ST.Order.confirm,
)

orders_window = Window( 
    Format('Ваши заказы:', when='exists'),
    ScrollingGroup(
        Select(
            Format('{item.product_name} - {item.quantity}\n' \
                   'Общая цена - {item.total_price}'),
            id="product_id",
            item_id_getter=lambda item: item.id, 
            items="products",
            on_click=on_orders_click,
            when='exists'
        ),
        id="scroll_orders",
        height=6,
        width=1,
    ),
    Button(
        Const("Заказать"),
        id="to_order",
        on_click=to_order,
        when='exists'
    ),
    Const('У вас нет заказов!\n' \
          'Заказать товары: /catalog', when=lambda data, widget, manager: not data["exists"]),
    getter=cart_getter,
    state=ST.Order.products
)

"""Окно тележки"""

cart_window = Window( 
    Format('Ваша корзина:\n' \
           'Стоимость - {cart_price}\n'
           'Нажмите на товар, чтоб удалить заказ',
           when='exists'),
    ScrollingGroup(
        Select(
            Format('{item.product_name} - {item.quantity}\n' \
                   'Общая цена - {item.total_price}'),
            id="product_id",
            item_id_getter=lambda item: item.id, 
            items="products",
            on_click=on_cart_click,
            when='exists'
        ),
        id="scroll_orders",
        height=6,
        width=1,
    ),
    Button(
        Const("Заказать"),
        id="to_order",
        on_click=to_order,
        when='exists'
    ),
    Const('Ваша корзина пуста! :C\n' \
          'Заказать товары: /catalog', when=lambda data, widget, manager: not data["exists"]),
    getter=cart_getter,
    state=ST.Cart.products
)

"""Окно заказа"""

order_window = Window(
    Format("{order_name} - {order_quantity} шт\nОбщая цена - {order_total_price}"),
    Button(
        Const("⬅ Назад"),
        id="go_back",
        on_click=go_back
    ),
    Button(
        Const("Удалить"),
        id="remove_order",
        on_click=remove_order
    ),
    getter=dialog_data_getter,
    state=ST.Cart.order
)

"""Окно категорий при обычном вызове каталога пользователем"""

categories_list = Window( 
    Format('Выберите категорию из доступных', when='exists'),
    ScrollingGroup(
        Select(
            Format('{item.name}'),
            id="category_id",
            item_id_getter=lambda item: item.category_id, 
            items="categories",
            on_click=on_category_click,
            when='exists'
        ),
        id="scroll_categories",
        height=6,
        width=1,
    ),
    Const('Нет доступных товаров', when=lambda data, widget, manager: not data["exists"]),
    getter=categories_getter,
    state=ST.Catalog.categories
)

"""Окно категорий при обычном вызове категории пользователем"""

products_window = Window(
    Format('Вы выбрали категорию: {category_name}\n'
          'Выберите товар:'),
    ScrollingGroup(
        Select(
            Format("{item.name} - {item.price} руб."),
            id="product_id",
            item_id_getter=lambda item: item.product_id,
            items="products",
            on_click=on_product_click,
            when='exists'
        ),
        id="scroll_products",
        height=6,
        width=1,
    ),
    Button(
        Const("⬅ Назад"),
        id="go_back",
        on_click=go_back
    ),
    Const('Нет доступных товаров', when=lambda data, widget, manager: not data["exists"]),
    getter=products_getter,
    state=ST.Catalog.products
)

"""Окно категорий при добавлении товара"""

add_product_window = Window(
    Format('Выберите категорию из доступных', when='exists'),
    ScrollingGroup(
        Select(
            Format('{item.name}'),
            id="category_id",
            item_id_getter=lambda item: item.category_id, 
            items="categories",
            on_click=product_adding,
            when='exists'
        ),
        id="scroll_categories",
        height=6,
        width=1,
    ),
    Const('Нет доступных товаров', when=lambda data, widget, manager: not data["exists"]),
    getter=categories_getter,
    state=ST.AddProduct.choice
)

"""Окно категорий при удалении категории"""

remove_category_window = Window(
    Format('Выберите категорию из доступных', when='exists'),
    ScrollingGroup(
        Select(
            Format('{item.name}'),
            id="category_id",
            item_id_getter=lambda item: item.category_id, 
            items="categories",
            on_click=on_confirm_category_remove,
            when='exists'
        ),
        id="scroll_categories",
        height=6,
        width=1,
    ),
    Const('Нет доступных товаров', when=lambda data, widget, manager: not data["exists"]),
    getter=categories_getter,
    state=ST.RemoveCategory.removing
)

"""Окно категорий при удалении товара"""

remove_products_categories_window = Window(
    Format('Выберите категорию из доступных', when='exists'),
    ScrollingGroup(
        Select(
            Format('{item.name}'),
            id="category_id",
            item_id_getter=lambda item: item.category_id, 
            items="categories",
            on_click=category_product_remove_click,
            when='exists'
        ),
        id="scroll_categories",
        height=6,
        width=1,
    ),
    Const('Нет доступных товаров', when=lambda data, widget, manager: not data["exists"]),
    getter=categories_getter,
    state=ST.RemoveProduct.choice_categories
)

"""Окно продуктов при удалении продуктов"""

remove_products_window = Window(
    Format('Вы выбрали категорию: {category_name}\n'
          'Выберите товар:'),
    ScrollingGroup(
        Select(
            Format("{item.name} - {item.price} руб."),
            id="product_id",
            item_id_getter=lambda item: item.product_id,
            items="products",
            on_click=on_confirm_product_remove,
            when='exists'
        ),
        id="scroll_products",
        height=6,
        width=1,
    ),
    Button(
        Const("⬅ Назад"),
        id="go_back",
        on_click=go_back
    ),
    Const('Нет доступных товаров', when=lambda data, widget, manager: not data["exists"]),
    getter=products_getter,
    state=ST.RemoveProduct.removing
)

edit_category_window = Window( 
    Format('Выберите категорию из доступных', when='exists'),
    ScrollingGroup(
        Select(
            Format('{item.name}'),
            id="category_id",
            item_id_getter=lambda item: item.category_id, 
            items="categories",
            on_click=category_edit_click,
            when='exists'
        ),
        id="scroll_categories",
        height=6,
        width=1,
    ),
    Const('Нет доступных товаров', when=lambda data, widget, manager: not data["exists"]),
    getter=categories_getter,
    state= ST.EditCategory.editing
)

edit_products_categories_window = Window( 
    Format('Выберите категорию из доступных', when='exists'),
    ScrollingGroup(
        Select(
            Format('{item.name}'),
            id="category_id",
            item_id_getter=lambda item: item.category_id, 
            items="categories",
            on_click=product_choice,
            when='exists'
        ),
        id="scroll_categories",
        height=6,
        width=1,
    ),
    Const('Нет доступных товаров', when=lambda data, widget, manager: not data["exists"]),
    getter=categories_getter,
    state= ST.EditProduct.choice_categories
)

edit_products_window = Window(
    Format('Вы выбрали категорию: {category_name}\n'
          'Выберите товар:'),
    ScrollingGroup(
        Select(
            Format("{item.name} - {item.price} руб."),
            id="product_id",
            item_id_getter=lambda item: item.product_id,
            items="products",
            on_click=edit_product_click,
            when='exists'
        ),
        id="scroll_products",
        height=6,
        width=1,
    ),
    Button(
        Const("⬅ Назад"),
        id="go_back",
        on_click=go_back
    ),
    Const('Нет доступных товаров', when=lambda data, widget, manager: not data["exists"]),
    getter=products_getter,
    state=ST.EditProduct.editing
)

choice_window = Window(
    Format("Нужно изменить цену или название товара?"),
    Row(
        Button(Const("Цену"), id="price", on_click=edit_product_price),
        Button(Const("Название"), id="name", on_click=edit_product_name)
    ),
    Button(
        Const("⬅ Назад"),
        id="go_back",
        on_click=go_back
    ),
    getter=dialog_data_getter,
    state=ST.EditProduct.price_or_name,
)

"Диалоги"

catalog_dialog = Dialog(
    categories_list,
    products_window,
)

add_product_dialog = Dialog(
    add_product_window
)

remove_category_dialog = Dialog(
    remove_category_window
)

remove_product_dialog = Dialog(
    remove_products_categories_window,
    remove_products_window
)

edit_category_dialog = Dialog(
    edit_category_window
)

edit_product_dialog = Dialog(
    edit_products_categories_window,
    edit_products_window,
    choice_window
)

cart_dialog = Dialog(
    cart_window,
    order_window
)

orders_dialog = Dialog(
    orders_window,
    decline_order
)