from aiogram import types
from aiogram.types.inline_keyboard_button import InlineKeyboardButton

keyboard_start = types.InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="пример команд", callback_data='command_example'),
        InlineKeyboardButton(text="info", callback_data='info')
    ]
])

keyboard_help = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Вы : Напомни купить зубную пасту завтра в 19:00", callback_data='reminder'),
            InlineKeyboardButton(text="Вы : Осадки Москва", callback_data='precipitation')]
    ])

keyboard_trash = types.InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🗑️", callback_data='precipitation')]
                                                                            ])
