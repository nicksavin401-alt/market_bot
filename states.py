from aiogram.fsm.state import State, StatesGroup


class Catalog(StatesGroup):
    categories = State()
    products = State()
    quantity = State()

class Cart(StatesGroup):
    products = State()
    order = State()
    location = State()
    confirm = State()

class Order(StatesGroup):
    products = State()
    confirm = State()

class AddCategory(StatesGroup):
    adding = State()

class AddProduct(StatesGroup):
    choice = State()
    name = State()
    price = State()

class RemoveCategory(StatesGroup):
    removing = State()
    confirm = State()

class RemoveProduct(StatesGroup):
    choice_categories = State()
    removing = State()
    confirm = State()

class EditCategory(StatesGroup):
    editing = State()
    name = State()

class EditProduct(StatesGroup):
    choice_categories = State()
    editing = State()
    price_or_name = State()
    name = State()
    price = State()
