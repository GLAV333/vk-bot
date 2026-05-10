from vkbottle import Bot, Message
from vkbottle.tools import BotKeyboard, KeyboardButtonColor
import datetime
import asyncio

VK_GROUP_TOKEN = "vk1.a.aWY8BgVcxtZhln7eXLvXEMNUwOrSRc_-s8prwws9n3cEdhzW17g3w3IZgES2VDRgTbi7AqI26WOEcuVr9dWhAWXB1aayvhLwmvyMxZZEtyriLwvJK3w7D6i3AUKJ-bRep6DrfEhOkOoiC9uGv1uFalzVxBelUushlfeWTRQFQsu2eg6Llo2fEkhmTMpEG4BNyNhLeYlCDlrifX7fxbOWsw"
VK_GROUP_ID = 238447439
ADMIN_ID = 138586192

bot = Bot(token=VK_GROUP_TOKEN)

user_orders = {}

def main_keyboard():
    kb = BotKeyboard()
    kb.add_button("📦 Заказать доставку", color=KeyboardButtonColor.POSITIVE)
    kb.add_row()
    kb.add_button("💰 Узнать цену", color=KeyboardButtonColor.SECONDARY)
    kb.add_row()
    kb.add_button("📋 Мои заказы", color=KeyboardButtonColor.DEFAULT)
    return kb

def delivery_type_keyboard():
    kb = BotKeyboard()
    kb.add_button("🏙️ По городу", color=KeyboardButtonColor.PRIMARY)
    kb.add_button("🌍 Межгород", color=KeyboardButtonColor.PRIMARY)
    return kb

@bot.on.private_message(text="старт")
async def start_handler(message: Message):
    await message.answer(
        "Здравствуйте!\n\n"
        "📦 Чтобы заказать доставку, нажмите кнопку «Заказать доставку» ниже.\n"
        "Наш бот поможет вам быстро оформить заказ.\n\n"
        "✅ После оформления заказа я отвечу вам в кратчайшие сроки, чтобы уточнить детали и рассчитать точную стоимость.\n\n"
        "💰 Тарифы:\n• По городу Владимир — от 500₽\n• Межгород — от 35₽/км",
        keyboard=main_keyboard()
    )

@bot.on.private_message(text="💰 Узнать цену")
async def price_handler(message: Message):
    await message.answer(
        "🚚 Наши тарифы:\n\n"
        "🏙️ Доставка по городу Владимир — от 500₽\n"
        "🌍 Межгород — от 35₽/км\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "⚠️ Доставка осуществляется легковыми автомобилями.\n"
        "📦 Ограничения по грузу:\n"
        "• Вес: до 100 кг\n"
        "• Высота: до 1 м\n"
        "• Длина: до 2 м\n"
        "• Ширина: до 1.3 м"
    )

@bot.on.private_message(text="📋 Мои заказы")
async def my_orders_handler(message: Message):
    user_id = message.from_id
    if user_id in user_orders and user_orders[user_id]:
        orders_list = "\n\n".join([f"📦 Заказ #{i+1}:\n{order}" for i, order in enumerate(user_orders[user_id])])
        await message.answer(f"📋 Ваши заказы:\n\n{orders_list}")
    else:
        await message.answer("📭 У вас пока нет заказов.\n\nЧтобы сделать заказ, нажмите «📦 Заказать доставку».")

@bot.on.private_message(text="📦 Заказать доставку")
async def order_start(message: Message):
    user_id = message.from_id
    if user_id not in user_orders:
        user_orders[user_id] = []
    if not hasattr(bot, "temp_orders"):
        bot.temp_orders = {}
    bot.temp_orders[user_id] = {"step": "awaiting_type"}
    await message.answer("Выберите тип доставки:", keyboard=delivery_type_keyboard())

@bot.on.private_message(text=["🏙️ По городу", "🌍 Межгород"])
async def delivery_type_handler(message: Message):
    user_id = message.from_id
    if not hasattr(bot, "temp_orders") or user_id not in bot.temp_orders:
        await message.answer("Начните заказ сначала: нажмите «📦 Заказать доставку»")
        return
    if message.text == "🏙️ По городу":
        bot.temp_orders[user_id]["type"] = "city"
        bot.temp_orders[user_id]["step"] = "awaiting_from_addr"
        await message.answer("Введите адрес отправления (улица, дом):")
    else:
        bot.temp_orders[user_id]["type"] = "intercity"
        bot.temp_orders[user_id]["step"] = "awaiting_from_city"
        await message.answer("Введите ГОРОД отправления:")

@bot.on.private_message()
async def order_steps(message: Message):
    user_id = message.from_id
    text = message.text
    if text in ["📦 Заказать доставку", "💰 Узнать цену", "📋 Мои заказы", "🏙️ По городу", "🌍 Межгород", "старт"]:
        return
    if not hasattr(bot, "temp_orders") or user_id not in bot.temp_orders:
        return
    
    step = bot.temp_orders[user_id].get("step")
    
    if step == "awaiting_from_addr":
        bot.temp_orders[user_id]["from_addr"] = text
        bot.temp_orders[user_id]["step"] = "awaiting_to_addr"
        await message.answer("Введите адрес доставки (улица, дом):")
    elif step == "awaiting_to_addr":
        bot.temp_orders[user_id]["to_addr"] = text
        bot.temp_orders[user_id]["step"] = "awaiting_cargo"
        await message.answer("Опишите груз (вес, габариты):")
    elif step == "awaiting_from_city":
        bot.temp_orders[user_id]["from_city"] = text
        bot.temp_orders[user_id]["step"] = "awaiting_from_addr_intercity"
        await message.answer("Введите АДРЕС в городе отправления:")
    elif step == "awaiting_from_addr_intercity":
        bot.temp_orders[user_id]["from_addr"] = text
        bot.temp_orders[user_id]["step"] = "awaiting_to_city"
        await message.answer("Введите ГОРОД назначения:")
    elif step == "awaiting_to_city":
        bot.temp_orders[user_id]["to_city"] = text
        bot.temp_orders[user_id]["step"] = "awaiting_to_addr_intercity"
        await message.answer("Введите АДРЕС в городе назначения:")
    elif step == "awaiting_to_addr_intercity":
        bot.temp_orders[user_id]["to_addr"] = text
        bot.temp_orders[user_id]["step"] = "awaiting_cargo"
        await message.answer("Опишите груз (вес, габариты):")
    elif step == "awaiting_cargo":
        bot.temp_orders[user_id]["cargo"] = text
        bot.temp_orders[user_id]["step"] = "awaiting_pickup"
        await message.answer("📅 Когда забрать груз?\n(например: сегодня до 18:00)")
    elif step == "awaiting_pickup":
        bot.temp_orders[user_id]["pickup"] = text
        bot.temp_orders[user_id]["step"] = "awaiting_delivery"
        await message.answer("📅 Когда доставить груз?\n(например: завтра к 12:00)")
    elif step == "awaiting_delivery":
        bot.temp_orders[user_id]["delivery"] = text
        order = bot.temp_orders[user_id]
        if order["type"] == "city":
            from_text = order["from_addr"]
            to_text = order["to_addr"]
            delivery_type_text = "По городу"
        else:
            from_text = f"{order['from_city']}, {order['from_addr']}"
            to_text = f"{order['to_city']}, {order['to_addr']}"
            delivery_type_text = "Межгород"
        
        order_summary = f"🚚 {delivery_type_text}\n📍 Откуда: {from_text}\n🏁 Куда: {to_text}\n📦 Груз: {order['cargo']}\n📅 Забрать: {order['pickup']}\n📅 Доставить: {order['delivery']}"
        user_orders[user_id].append(order_summary)
        
        if user_id != ADMIN_ID:
            user_info = await bot.api.users.get(user_ids=user_id)
            user_name = f"{user_info[0].first_name} {user_info[0].last_name}" if user_info else f"id{user_id}"
            await bot.api.messages.send(
                peer_id=ADMIN_ID,
                message=f"🔔 НОВЫЙ ЗАКАЗ!\n\n👤 Клиент: {user_name}\n🔗 Ссылка: vk.com/id{user_id}\n🚚 Тип: {delivery_type_text}\n📍 Откуда: {from_text}\n🏁 Куда: {to_text}\n📦 Груз: {order['cargo']}\n📅 Забрать: {order['pickup']}\n📅 Доставить: {order['delivery']}",
                random_id=0
            )
        
        await message.answer(
            f"✨ Спасибо за заказ! ✨\n\n✅ Заказ принят!\n\n📋 Детали:\n📍 Откуда: {from_text}\n🏁 Куда: {to_text}\n📦 Груз: {order['cargo']}\n📅 Забрать: {order['pickup']}\n📅 Доставить: {order['delivery']}\n\n💰 Стоимость рассчитаю и сообщу вам в ближайшее время.",
            keyboard=main_keyboard()
        )
        del bot.temp_orders[user_id]

print("✅ Бот ВКонтакте успешно запущен!")
bot.run_polling()
