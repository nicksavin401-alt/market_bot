import dialogs.dialog_callbacks as dialog_callbacks
import dialogs.dialog_getters as dialog_getters
import states as states
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Button, Row, Back
from aiogram_dialog.widgets.text import Format, Const

"""Окна"""

decline_order = Window(
    Format("Отменить заказ?"),
    Row(
        Button(
            Const("Отменить"), id="decline", on_click=dialog_callbacks.order_decline
        ),
        Back(Const("⬅ Назад"), id="go_back"),
    ),
    getter=dialog_getters.dialog_data_getter,
    state=states.Order.confirm,
)

orders_window = Window(
    Format("Ваши заказы:", when="exists"),
    ScrollingGroup(
        Select(
            Format(
                "{item.product_name} - {item.quantity} шт.\n"
                "Общая цена - {item.total_price} руб."
            ),
            id="product_id",
            item_id_getter=lambda item: item.id,
            items="products",
            on_click=dialog_callbacks.on_orders_click,
            when="exists",
        ),
        id="scroll_orders",
        height=6,
        width=1,
    ),
    Const(
        "У вас нет заказов!\n" "Заказать товары: /catalog",
        when=lambda data, widget, manager: not data["exists"],
    ),
    getter=dialog_getters.order_getter,
    state=states.Order.products,
)

"""Окно тележки"""

cart_window = Window(
    Format(
        "Ваша корзина:\n"
        "Стоимость - {cart_price} руб.\n"
        "Нажмите на товар, чтоб удалить заказ",
        when="exists",
    ),
    ScrollingGroup(
        Select(
            Format(
                "{item.product_name} - {item.quantity}\n"
                "Общая цена - {item.total_price} руб."
            ),
            id="product_id",
            item_id_getter=lambda item: item.id,
            items="products",
            on_click=dialog_callbacks.on_cart_click,
            when="exists",
        ),
        id="scroll_orders",
        height=6,
        width=1,
    ),
    Button(
        Const("Заказать"),
        id="to_order",
        on_click=dialog_callbacks.to_order,
        when="exists",
    ),
    Const(
        "Ваша корзина пуста! :C\n" "Заказать товары: /catalog",
        when=lambda data, widget, manager: not data["exists"],
    ),
    getter=dialog_getters.cart_getter,
    state=states.Cart.products,
)

"""Окно заказа"""

order_window = Window(
    Format("{cart_name} - {cart_quantity} шт\nОбщая цена - {cart_total_price} руб."),
    Back(Const("⬅ Назад"), id="go_back"),
    Button(Const("Удалить"), id="remove_order", on_click=dialog_callbacks.remove_order),
    getter=dialog_getters.dialog_data_getter,
    state=states.Cart.order,
)

"""Окно категорий при обычном вызове каталога пользователем"""

categories_list = Window(
    Format("Выберите категорию из доступных", when="exists"),
    ScrollingGroup(
        Select(
            Format("{item.name}"),
            id="category_id",
            item_id_getter=lambda item: item.category_id,
            items="categories",
            on_click=dialog_callbacks.on_category_click,
            when="exists",
        ),
        id="scroll_categories",
        height=6,
        width=1,
    ),
    Const(
        "Нет доступных товаров", when=lambda data, widget, manager: not data["exists"]
    ),
    getter=dialog_getters.categories_getter,
    state=states.Catalog.categories,
)

"""Окно категорий при обычном вызове категории пользователем"""

products_window = Window(
    Format("Вы выбрали категорию: {category_name}\n" "Выберите товар:"),
    ScrollingGroup(
        Select(
            Format("{item.name} - {item.price} руб."),
            id="product_id",
            item_id_getter=lambda item: item.product_id,
            items="products",
            on_click=dialog_callbacks.on_product_click,
            when="exists",
        ),
        id="scroll_products",
        height=6,
        width=1,
    ),
    Back(Const("⬅ Назад"), id="go_back"),
    Const(
        "Нет доступных товаров", when=lambda data, widget, manager: not data["exists"]
    ),
    getter=dialog_getters.products_getter,
    state=states.Catalog.products,
)

"""Окно категорий при добавлении товара"""

add_product_window = Window(
    Format("Выберите категорию из доступных", when="exists"),
    ScrollingGroup(
        Select(
            Format("{item.name}"),
            id="category_id",
            item_id_getter=lambda item: item.category_id,
            items="categories",
            on_click=dialog_callbacks.product_adding,
            when="exists",
        ),
        id="scroll_categories",
        height=6,
        width=1,
    ),
    Const(
        "Нет доступных товаров", when=lambda data, widget, manager: not data["exists"]
    ),
    getter=dialog_getters.categories_getter,
    state=states.AddProduct.choice,
)

"""Окно категорий при удалении категории"""

remove_category_window = Window(
    Format("Выберите категорию из доступных", when="exists"),
    ScrollingGroup(
        Select(
            Format("{item.name}"),
            id="category_id",
            item_id_getter=lambda item: item.category_id,
            items="categories",
            on_click=dialog_callbacks.on_confirm_category_remove,
            when="exists",
        ),
        id="scroll_categories",
        height=6,
        width=1,
    ),
    Const(
        "Нет доступных товаров", when=lambda data, widget, manager: not data["exists"]
    ),
    getter=dialog_getters.categories_getter,
    state=states.RemoveCategory.removing,
)

"""Окно категорий при удалении товара"""

remove_products_categories_window = Window(
    Format("Выберите категорию из доступных", when="exists"),
    ScrollingGroup(
        Select(
            Format("{item.name}"),
            id="category_id",
            item_id_getter=lambda item: item.category_id,
            items="categories",
            on_click=dialog_callbacks.category_product_remove_click,
            when="exists",
        ),
        id="scroll_categories",
        height=6,
        width=1,
    ),
    Const(
        "Нет доступных товаров", when=lambda data, widget, manager: not data["exists"]
    ),
    getter=dialog_getters.categories_getter,
    state=states.RemoveProduct.choice_categories,
)

"""Окно продуктов при удалении продуктов"""

remove_products_window = Window(
    Format("Вы выбрали категорию: {category_name}\n" "Выберите товар:"),
    ScrollingGroup(
        Select(
            Format("{item.name} - {item.price} руб."),
            id="product_id",
            item_id_getter=lambda item: item.product_id,
            items="products",
            on_click=dialog_callbacks.on_confirm_product_remove,
            when="exists",
        ),
        id="scroll_products",
        height=6,
        width=1,
    ),
    Back(Const("⬅ Назад"), id="go_back"),
    Const(
        "Нет доступных товаров", when=lambda data, widget, manager: not data["exists"]
    ),
    getter=dialog_getters.products_getter,
    state=states.RemoveProduct.removing,
)

edit_category_window = Window(
    Format("Выберите категорию из доступных", when="exists"),
    ScrollingGroup(
        Select(
            Format("{item.name}"),
            id="category_id",
            item_id_getter=lambda item: item.category_id,
            items="categories",
            on_click=dialog_callbacks.category_edit_click,
            when="exists",
        ),
        id="scroll_categories",
        height=6,
        width=1,
    ),
    Const(
        "Нет доступных товаров", when=lambda data, widget, manager: not data["exists"]
    ),
    getter=dialog_getters.categories_getter,
    state=states.EditCategory.editing,
)

edit_products_categories_window = Window(
    Format("Выберите категорию из доступных", when="exists"),
    ScrollingGroup(
        Select(
            Format("{item.name}"),
            id="category_id",
            item_id_getter=lambda item: item.category_id,
            items="categories",
            on_click=dialog_callbacks.product_choice,
            when="exists",
        ),
        id="scroll_categories",
        height=6,
        width=1,
    ),
    Const(
        "Нет доступных товаров", when=lambda data, widget, manager: not data["exists"]
    ),
    getter=dialog_getters.categories_getter,
    state=states.EditProduct.choice_categories,
)

edit_products_window = Window(
    Format("Вы выбрали категорию: {category_name}\n" "Выберите товар:"),
    ScrollingGroup(
        Select(
            Format("{item.name} - {item.price} руб."),
            id="product_id",
            item_id_getter=lambda item: item.product_id,
            items="products",
            on_click=dialog_callbacks.edit_product_click,
            when="exists",
        ),
        id="scroll_products",
        height=6,
        width=1,
    ),
    Back(Const("⬅ Назад"), id="go_back"),
    Const(
        "Нет доступных товаров", when=lambda data, widget, manager: not data["exists"]
    ),
    getter=dialog_getters.products_getter,
    state=states.EditProduct.editing,
)

choice_window = Window(
    Format("Нужно изменить цену или название товара?"),
    Row(
        Button(Const("Цену"), id="price", on_click=dialog_callbacks.edit_product_price),
        Button(
            Const("Название"), id="name", on_click=dialog_callbacks.edit_product_name
        ),
    ),
    Back(Const("⬅ Назад"), id="go_back"),
    getter=dialog_getters.dialog_data_getter,
    state=states.EditProduct.price_or_name,
)
