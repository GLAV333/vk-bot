import requests
import time
import json
import random

VK_GROUP_TOKEN = "vk1.a.aWY8BgVcxtZhln7eXLvXEMNUwOrSRc_-s8prwws9n3cEdhzW17g3w3IZgES2VDRgTbi7AqI26WOEcuVr9dWhAWXB1aayvhLwmvyMxZZEtyriLwvJK3w7D6i3AUKJ-bRep6DrfEhOkOoiC9uGv1uFalzVxBelUushlfeWTRQFQsu2eg6Llo2fEkhmTMpEG4BNyNhLeYlCDlrifX7fxbOWsw"  # Вставьте свой токен
VK_GROUP_ID = 238447439  # Вставьте ID сообщества

API_VERSION = "5.199"

# Хранилище данных пользователей (в оперативной памяти)
user_data = {}
# Хранилище заказов
orders = {}
order_counter = 1

def send_message(peer_id, text, keyboard=None):
    url = "https://api.vk.com/method/messages.send"
    payload = {
        "access_token": VK_GROUP_TOKEN,
        "v": API_VERSION,
        "peer_id": peer_id,
        "message": text,
        "random_id": random.randint(1, 999999999)
    }
    if keyboard:
        payload["keyboard"] = json.dumps(keyboard)
    requests.post(url, data=payload)

# Клавиатура главного меню
def get_main_keyboard():
    return {
        "one_time": False,
        "buttons": [
            [{"action": {"type": "text", "label": "📦 Заказать доставку"}, "color": "positive"}],
            [{"action": {"type": "text", "label": "💰 Узнать цену"}, "color": "secondary"}],
            [{"action": {"type": "text", "label": "📋 Мои заказы"}, "color": "default"}],
            [{"action": {"type": "text", "label": "ℹ️ Мои данные"}, "color": "secondary"}]
        ]
    }

# Клавиатура выбора типа доставки
def get_delivery_type_keyboard():
    return {
        "one_time": True,
        "buttons": [
            [{"action": {"type": "text", "label": "🏙️ Доставка по городу"}, "color": "positive"}],
            [{"action": {"type": "text", "label": "🌍 Межгород"}, "color": "positive"}]
        ]
    }

def get_status_text(status):
    statuses = {
        'new': '🆕 Новый',
        'processing': '🔄 В обработке',
        'delivering': '🚚 В пути',
        'completed': '✅ Доставлен'
    }
    return statuses.get(status, '🆕 Новый')

print("✅ Бот ВКонтакте запущен и слушает Long Poll...")

# Получаем Long Poll сервер
server_url = None
key = None
ts = None

while True:
    if not server_url:
        resp = requests.get("https://api.vk.com/method/groups.getLongPollServer", params={
            "access_token": VK_GROUP_TOKEN,
            "v": API_VERSION,
            "group_id": VK_GROUP_ID
        }).json()
        if "response" in resp:
            data = resp["response"]
            server_url = data["server"]
            key = data["key"]
            ts = data["ts"]
            print("Long Poll сервер получен")
        else:
            print("Ошибка получения сервера:", resp)
            time.sleep(5)
            continue

    try:
        resp = requests.get(server_url, params={
            "act": "a_check",
            "key": key,
            "ts": ts,
            "wait": 25
        }).json()
    except Exception as e:
        print("Ошибка запроса:", e)
        server_url = None
        continue

    if "failed" in resp:
        print("Long Poll failed, переподключаемся")
        server_url = None
        time.sleep(1)
        continue

    ts = resp["ts"]
    updates = resp.get("updates", [])
    for upd in updates:
        if upd.get("type") == "message_new":
            msg = upd["object"]["message"]
            peer_id = msg["peer_id"]
            text = msg.get("text", "")
            user_id = peer_id

            # Инициализация данных пользователя
            if user_id not in user_data:
                user_data[user_id] = {}

            state = user_data[user_id].get("state", "none")

            # Обработка команды /start
            if text == "/start":
                if user_data[user_id].get("phone"):
                    send_message(peer_id, f"С возвращением, {user_data[user_id].get('name', 'пользователь')}!", keyboard=get_main_keyboard())
                else:
                    send_message(peer_id, "👋 Привет! Я бот доставки.\nДля регистрации отправьте ваш номер телефона:")
                    user_data[user_id]["state"] = "awaiting_phone"

            # Регистрация: ожидание номера телефона
            elif state == "awaiting_phone":
                user_data[user_id]["phone"] = text
                user_data[user_id]["state"] = "awaiting_name"
                send_message(peer_id, "📝 Введите ваше ИМЯ (как к вам обращаться):")

            # Регистрация: ожидание имени
            elif state == "awaiting_name":
                user_data[user_id]["name"] = text
                user_data[user_id]["state"] = "registered"
                send_message(peer_id, f"✅ Регистрация успешна, {text}!\n📞 Телефон: {user_data[user_id]['phone']}", keyboard=get_main_keyboard())

            # Обработка кнопки "Заказать доставку"
            elif text == "📦 Заказать доставку":
                if user_data[user_id].get("state") != "registered":
                    send_message(peer_id, "Сначала зарегистрируйтесь — отправьте /start")
                else:
                    user_data[user_id]["state"] = "awaiting_delivery_type"
                    send_message(peer_id, "Выберите тип доставки:", keyboard=get_delivery_type_keyboard())

            # Выбор типа доставки: по городу
            elif text == "🏙️ Доставка по городу":
                user_data[user_id]["delivery_type"] = "city"
                user_data[user_id]["state"] = "awaiting_city_from_address"
                send_message(peer_id, "Введите адрес отправления (улица, дом):")

            # Выбор типа доставки: межгород
            elif text == "🌍 Межгород":
                user_data[user_id]["delivery_type"] = "intercity"
                user_data[user_id]["state"] = "awaiting_intercity_from_city"
                send_message(peer_id, "Введите ГОРОД отправления:")

            # Логика заказа
            elif state == "awaiting_city_from_address":
                user_data[user_id]["from_address"] = text
                user_data[user_id]["state"] = "awaiting_city_to_address"
                send_message(peer_id, "Введите адрес доставки (улица, дом):")
            elif state == "awaiting_city_to_address":
                user_data[user_id]["to_address"] = text
                user_data[user_id]["state"] = "awaiting_cargo"
                send_message(peer_id, "Опишите груз (вес, габариты):")
            elif state == "awaiting_intercity_from_city":
                user_data[user_id]["from_city"] = text
                user_data[user_id]["state"] = "awaiting_intercity_from_address"
                send_message(peer_id, "Введите АДРЕС в городе отправления:")
            elif state == "awaiting_intercity_from_address":
                user_data[user_id]["from_address"] = text
                user_data[user_id]["state"] = "awaiting_intercity_to_city"
                send_message(peer_id, "Введите ГОРОД назначения:")
            elif state == "awaiting_intercity_to_city":
                user_data[user_id]["to_city"] = text
                user_data[user_id]["state"] = "awaiting_intercity_to_address"
                send_message(peer_id, "Введите АДРЕС в городе назначения:")
            elif state == "awaiting_intercity_to_address":
                user_data[user_id]["to_address"] = text
                user_data[user_id]["state"] = "awaiting_cargo"
                send_message(peer_id, "Опишите груз (вес, габариты):")
            elif state == "awaiting_cargo":
                user_data[user_id]["cargo"] = text
                user_data[user_id]["state"] = "awaiting_pickup"
                send_message(peer_id, "📅 Когда забрать груз?\n(например: сегодня до 18:00)")
            elif state == "awaiting_pickup":
                user_data[user_id]["pickup"] = text
                user_data[user_id]["state"] = "awaiting_delivery"
                send_message(peer_id, "📅 Когда доставить груз?\n(например: завтра к 12:00)")
            elif state == "awaiting_delivery":
                user_data[user_id]["delivery"] = text

                global order_counter
                order_id = order_counter
                order_counter += 1

                delivery_type = user_data[user_id]["delivery_type"]
                if delivery_type == "city":
                    from_loc = user_data[user_id]["from_address"]
                    to_loc = user_data[user_id]["to_address"]
                else:
                    from_loc = f"{user_data[user_id]['from_city']}, {user_data[user_id]['from_address']}"
                    to_loc = f"{user_data[user_id]['to_city']}, {user_data[user_id]['to_address']}"

                orders[order_id] = {
                    "order_id": order_id,
                    "user_id": user_id,
                    "delivery_type": delivery_type,
                    "from_loc": from_loc,
                    "to_loc": to_loc,
                    "cargo": user_data[user_id]["cargo"],
                    "pickup": user_data[user_id]["pickup"],
                    "delivery": user_data[user_id]["delivery"],
                    "status": "new",
                    "customer_name": user_data[user_id].get("name"),
                    "customer_phone": user_data[user_id].get("phone")
                }

                if "my_orders" not in user_data[user_id]:
                    user_data[user_id]["my_orders"] = []
                user_data[user_id]["my_orders"].append(order_id)

                delivery_text = "🏙️ Доставка по городу" if delivery_type == "city" else "🌍 Межгород"

                send_message(peer_id, f"✨ Спасибо за доверие! ✨\n\n✅ Ваш заказ №{order_id} уже в работе.\n\n📋 Детали заказа:\n🚚 Тип: {delivery_text}\n📍 Откуда: {from_loc}\n🏁 Куда: {to_loc}\n📦 Груз: {user_data[user_id]['cargo']}\n📅 Забор: {user_data[user_id]['pickup']}\n📅 Доставка: {user_data[user_id]['delivery']}\n\n💰 Стоимость сообщит оператор.\n\n📞 Оператор свяжется с вами!", keyboard=get_main_keyboard())

                # Уведомление админу (вставьте свой ID ВК)
                ADMIN_ID = 123456789  # Вставьте свой числовой ID ВК
                admin_message = f"🔔 НОВЫЙ ЗАКАЗ #{order_id}!\n\n👤 Клиент: {user_data[user_id].get('name')}\n📞 Телефон: {user_data[user_id].get('phone')}\n🚚 Тип: {delivery_text}\n📍 {from_loc} → {to_loc}\n📦 {user_data[user_id]['cargo']}\n📅 Забор: {user_data[user_id]['pickup']}\n📅 Доставка: {user_data[user_id]['delivery']}"
                send_message(ADMIN_ID, admin_message)

                user_data[user_id]["state"] = "registered"

            # Кнопка "Узнать цену"
            elif text == "💰 Узнать цену":
                send_message(peer_id, "🚚 Наши тарифы:\n\n🏙️ Доставка по городу Владимир\nот 500 рублей\n\n🌍 Межгород\nот 35 руб/км\n\n━━━━━━━━━━━━━━━━━━\n⚠️ Доставка осуществляется легковыми автомобилями.\n\n📦 Ограничения:\n• Вес: до 100 кг\n• Высота: до 1 м\n• Длина: до 2 м\n• Ширина: до 1.3 м\n\n📞 Для точного расчёта свяжитесь с оператором")

            # Кнопка "Мои заказы"
            elif text == "📋 Мои заказы":
                my_orders_ids = user_data[user_id].get("my_orders", [])
                if not my_orders_ids:
                    send_message(peer_id, "📭 У вас пока нет заказов.", keyboard=get_main_keyboard())
                else:
                    result = "📋 Ваши заказы:\n\n"
                    for oid in my_orders_ids:
                        if oid in orders:
                            o = orders[oid]
                            delivery_type_text = "🏙️ По городу" if o["delivery_type"] == "city" else "🌍 Межгород"
                            result += f"📦 Заказ #{oid} | {delivery_type_text}\n📍 {o['from_loc']} → {o['to_loc']}\n📊 Статус: {get_status_text(o['status'])}\n────────────────────\n"
                    send_message(peer_id, result, keyboard=get_main_keyboard())

            # Кнопка "Мои данные"
            elif text == "ℹ️ Мои данные":
                if user_data[user_id].get("state") == "registered":
                    send_message(peer_id, f"👤 Имя: {user_data[user_id].get('name')}\n📞 Телефон: {user_data[user_id].get('phone')}", keyboard=get_main_keyboard())
                else:
                    send_message(peer_id, "Вы не зарегистрированы. Отправьте /start")

            # Нераспознанная команда
            else:
                if user_data[user_id].get("state") == "registered":
                    send_message(peer_id, "Используйте кнопки меню.", keyboard=get_main_keyboard())
                else:
                    send_message(peer_id, "Отправьте /start для регистрации")
