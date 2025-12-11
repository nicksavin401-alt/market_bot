import dialogs.windows as windows
from aiogram_dialog import Dialog

"Диалоги"

catalog_dialog = Dialog(
    windows.categories_list,
    windows.products_window,
)

add_product_dialog = Dialog(windows.add_product_window)

remove_category_dialog = Dialog(windows.remove_category_window)

remove_product_dialog = Dialog(
    windows.remove_products_categories_window, windows.remove_products_window
)

edit_category_dialog = Dialog(windows.edit_category_window)

edit_product_dialog = Dialog(
    windows.edit_products_categories_window,
    windows.edit_products_window,
    windows.choice_window,
)

cart_dialog = Dialog(windows.cart_window, windows.order_window)

orders_dialog = Dialog(windows.orders_window, windows.decline_order)
