from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    kb = [
        [KeyboardButton(text="📞 Nomer olish"), KeyboardButton(text="🛍️ Buyurtma Berish")],
        [KeyboardButton(text="🛒 Buyurtmalarim"), KeyboardButton(text="💳 Hisobim")],
        [KeyboardButton(text="📩 Hisob To'ldirish"), KeyboardButton(text="💸 Pul Ishlash")],
        [KeyboardButton(text="📕 Qo'llanma"), KeyboardButton(text="☎️ Qo'llab-quvvatlash")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def admin_menu():
    kb = [
        [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="✉️ Xabar yuborish")],
        [KeyboardButton(text="💰 Balans qo'shish"), KeyboardButton(text="🔙 Asosiy menyu")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
