from vkbottle import Bot, Message
from vkbottle.tools import BotKeyboard, KeyboardButtonColor
from vkbottle_types import BaseModel

# Ваши данные (ОБЯЗАТЕЛЬНО ЗАМЕНИТЕ НА СВОИ!)
VK_GROUP_TOKEN = "vk1.a.aWY8BgVcxtZhln7eXLvXEMNUwOrSRc_-s8prwws9n3cEdhzW17g3w3IZgES2VDRgTbi7AqI26WOEcuVr9dWhAWXB1aayvhLwmvyMxZZEtyriLwvJK3w7D6i3AUKJ-bRep6DrfEhOkOoiC9uGv1uFalzVxBelUushlfeWTRQFQsu2eg6Llo2fEkhmTMpEG4BNyNhLeYlCDlrifX7fxbOWsw"  # Ваш токен в кавычках
VK_GROUP_ID = 238447439  # Ваш ID сообщества (только цифры)

# Добавляем класс для исправления ошибки
class StatePeer(BaseModel):
    id: int
    type: str

bot = Bot(token=VK_GROUP_TOKEN)

# Клавиатура
def main_keyboard():
    kb = BotKeyboard()
    kb.add_button("📦 Заказать", color=KeyboardButtonColor.POSITIVE)
    kb.add_button("💰 Цена", color=KeyboardButtonColor.SECONDARY)
    kb.add_row()
    kb.add_button("📋 Мои заказы", color=KeyboardButtonColor.DEFAULT)
    kb.add_button("ℹ️ Данные", color=KeyboardButtonColor.SECONDARY)
    return kb

@bot.on.private_message(text="/start")
async def start(message: Message):
    await message.answer("Привет! Я бот доставки.", keyboard=main_keyboard())

@bot.on.private_message(text="💰 Цена")
async def price(message: Message):
    await message.answer("Тарифы: по городу от 500₽, межгород от 35₽/км")

@bot.on.private_message(text="📦 Заказать")
async def order(message: Message):
    await message.answer("🚧 Заказы скоро появятся!")

@bot.on.private_message(text="📋 Мои заказы")
async def orders(message: Message):
    await message.answer("У вас пока нет заказов.")

@bot.on.private_message(text="ℹ️ Данные")
async def data(message: Message):
    await message.answer("Вы не зарегистрированы. Скоро добавим регистрацию.")

print("✅ Бот ВКонтакте запущен!")
bot.run_polling()





