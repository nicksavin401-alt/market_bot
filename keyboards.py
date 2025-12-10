from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

catalog = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Каталог")]],
    resize_keyboard=True, 
    one_time_keyboard=True,
)

location_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да, подтвердить",
                    callback_data="confirm_address"
                ),
                InlineKeyboardButton(
                    text="✏️ Изменить адрес", 
                    callback_data="change_address"
                )
            ]
        ])

confirm_payment_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да, подтвердить",
                    callback_data="confirm_payment"
                ),
                InlineKeyboardButton(
                    text="❌ Отменить", 
                    callback_data="reject_payment"
                )
            ]
        ])

 # Инлайн-кнопка для администратора (для ручной проверки)
admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text = "✅ Подтвердить оплату",
            callback_data="admin_confirm"
        ),
        InlineKeyboardButton(
            text = "❌ Отменить", 
            callback_data="admin_reject"
        )
    ]
])
