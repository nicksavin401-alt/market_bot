from database.models import async_session, User, Admin, Category, Cart, Product, Order
from sqlalchemy import or_, and_, select, update, delete


async def create_user_profile(new_tg_id):
    """Создание пользователя в бд (вызывается только по командах /start, Старт)"""
    async with async_session() as session:
        try:
            existing = await session.scalar(
                select(User).where(User.tg_id == new_tg_id)
            )  # проверка на существование пользователя

            if existing:
                return

            new_user = User(tg_id=new_tg_id)
            session.add(new_user)
            await session.commit()
        except Exception as e:
            await session.rollback()
            print(f"Ошибка при создании пользователя: {e}")


async def check_admin(new_tg_id) -> bool:
    """Проверка админ-доступа"""
    async with async_session() as session:
        user = await session.scalar(select(Admin).where(Admin.tg_id == new_tg_id))
        return user

async def categories_getter():
    async with async_session() as session:
        result = await session.execute(select(Category))
        categories = result.scalars().all()  # получаем список объектов Category
    return categories


async def categories_setter(new_category):
    async with async_session() as session:
        session.add(Category(name=new_category))
        await session.commit()


async def remove_category(category_id: int) -> bool:
    async with async_session() as session:
        category = await session.get(Category, category_id)

        if not category:
            return False

        await session.execute(delete(Product).where(Product.category_id == category_id))
        await session.delete(category)
        await session.commit()
        return True


async def remove_product(product_id: int) -> bool:
    async with async_session() as session:
        product = await session.get(Product, product_id)

        if not product:
            return False

        await session.delete(product)
        await session.commit()
        return True


async def products_getter():
    async with async_session() as session:
        result = await session.execute(select(Product))
        products = result.scalars().all()  # получаем список объектов Product
    return products


async def products_setter(new_product, new_price, new_category_id):
    async with async_session() as session:
        session.add(
            Product(name=new_product, price=new_price, category_id=new_category_id)
        )
        await session.commit()


async def update_category_name(category_id: int, new_name: str) -> bool:
    async with async_session() as session:
        category = await session.get(Category, category_id)

        if not category:
            return False

        category.name = new_name

        await session.commit()
        return True


async def update_product(product_id: int, **kwargs) -> bool:
    async with async_session() as session:
        product = await session.get(Product, product_id)

        if not product:
            return False

        # Устанавливаем только те поля, которые реально существуют в модели
        for field, value in kwargs.items():
            if hasattr(product, field):
                setattr(product, field, value)

        await session.commit()
        return True



async def add_to_cart(product_id: int, user_id: int, quantity=int) -> bool:
    async with async_session() as session:
        product = await session.scalar(
            select(Product).where(Product.product_id == product_id)
        )
        added_price = product.price
        added_name = product.name
        session.add(
            Cart(
                product_id=product_id,
                user_id=user_id,
                quantity=quantity,
                added_price=added_price,
                product_name=added_name,
            )
        )
        await session.commit()


async def cart_getter(user_id):
    async with async_session() as session:
        result = await session.execute(select(Cart).where(Cart.user_id == user_id))
        products = result.scalars().all()
    return products


async def orders_getter(user_id):
    async with async_session() as session:
        result = await session.execute(select(Order).where(Order.user_id == user_id))
        products = result.scalars().all()
    return products


async def getter_cart_amount(user_id):
    async with async_session() as session:
        result = await session.execute(select(Cart).where(Cart.user_id == user_id))
        products = result.scalars().all()

    cart_price = 0
    for product in products:
        product.total_price = product.quantity * int(product.added_price)
        cart_price += product.total_price

    return cart_price


async def cart_order_getter(id):
    async with async_session() as session:
        product = await session.get(Cart, id)
    return product


async def order_getter(id):
    async with async_session() as session:
        product = await session.get(Order, id)
    return product


async def remove_cart(order_id: int) -> bool:
    async with async_session() as session:
        order = await session.get(Cart, order_id)

        if not order:
            return False

        await session.delete(order)
        await session.commit()
        return True


async def remove_order(order_id: int) -> bool:
    async with async_session() as session:
        order = await session.get(Order, order_id)

        if not order:
            return False

        await session.delete(order)
        await session.commit()
        return True


async def transfer_cart_to_orders(user_id: int) -> bool:
    """
    Переносит все товары из корзины в заказы и очищает корзину
    Возвращает True если операция успешна, False если корзина пуста
    """
    async with async_session() as session:
        try:
            # 1. Получаем все товары из корзины пользователя
            stmt = select(Cart).where(Cart.user_id == user_id)
            result = await session.execute(stmt)
            cart_items = result.scalars().all()

            # Если корзина пуста
            if not cart_items:
                return False

            # 2. Переносим каждый товар из корзины в заказы
            for cart_item in cart_items:
                # Создаем аналогичную запись в таблице Order
                order_item = Order(
                    user_id=cart_item.user_id,
                    product_id=cart_item.product_id,
                    product_name=cart_item.product_name,
                    quantity=cart_item.quantity,
                    added_price=cart_item.added_price,
                )
                session.add(order_item)

            # 3. Удаляем все товары из корзины пользователя
            delete_stmt = delete(Cart).where(Cart.user_id == user_id)
            await session.execute(delete_stmt)

            # 4. Сохраняем изменения
            await session.commit()

            return True

        except Exception as e:
            await session.rollback()
            print(f"Ошибка при переносе корзины в заказы: {e}")
            return False
