import database.requests as requests
from aiogram_dialog import DialogManager


async def categories_getter(dialog_manager: DialogManager, **kwargs):
    categories = await requests.categories_getter()
    return {"categories": categories, "exists": bool(categories)}


async def products_getter(dialog_manager: DialogManager, **kwargs):
    # Получаем ID выбранной категории из dialog_data
    category_id = dialog_manager.dialog_data.get("category_id")
    category_name = dialog_manager.dialog_data.get("category_name")

    # База данных товаров по категориям
    all_products = await requests.products_getter()

    products = []
    for p in all_products:
        if p.category_id == int(category_id):
            products.append(p)

    return {
        "products": products,
        "exists": bool(products),
        "category_id": category_id,
        "category_name": category_name,
    }


async def cart_getter(dialog_manager: DialogManager, **kwargs):

    user_id = dialog_manager.event.from_user.id
    # База данных товаров по id
    products = await requests.cart_getter(user_id)
    cart_price = 0

    for product in products:
        product.total_price = product.quantity * int(product.added_price)
        cart_price += product.total_price

    return {"products": products, "exists": bool(products), "cart_price": cart_price}


async def order_getter(dialog_manager: DialogManager, **kwargs):

    user_id = dialog_manager.event.from_user.id
    # База данных товаров по id
    products = await requests.orders_getter(user_id)
    total_price = 0

    for product in products:
        product.total_price = product.quantity * int(product.added_price)
        total_price += product.total_price

    return {"products": products, "exists": bool(products), "cart_price": total_price}


async def dialog_data_getter(dialog_manager: DialogManager, **kwargs):
    return dialog_manager.dialog_data
