from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from typing import List

engine = create_async_engine(url="sqlite+aiosqlite:///database/db.sqlite3", echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # id в Telegram


class Admin(Base):
    __tablename__ = "admins"

    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # id в Telegram


class Category(Base):
    __tablename__ = "categories"

    category_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    products: Mapped[List["Product"]] = relationship(
        back_populates="category"
    )  # ORM связь с продуктами


class Product(Base):
    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.category_id"))
    name: Mapped[str] = mapped_column()
    price: Mapped[float] = mapped_column()
    category: Mapped["Category"] = relationship(
        back_populates="products"
    )  # ORM связь с категорией


class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    product_name: Mapped[str] = mapped_column()  # имя на момент добавления
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.product_id"),  # связь с Product по product_id
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(default=1)
    added_price: Mapped[float] = mapped_column()  # цена на момент добавления


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    product_name: Mapped[str] = mapped_column()  # имя на момент добавления
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.product_id"),  # связь с Product по product_id
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(default=1)
    added_price: Mapped[float] = mapped_column()  # цена на момент добавления
    delivered: Mapped[bool] = mapped_column(default=False)


async def db_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
