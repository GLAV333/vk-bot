import requests
import time
import json

VK_GROUP_TOKEN = "vk1.a.aWY8BgVcxtZhln7eXLvXEMNUwOrSRc_-s8prwws9n3cEdhzW17g3w3IZgES2VDRgTbi7AqI26WOEcuVr9dWhAWXB1aayvhLwmvyMxZZEtyriLwvJK3w7D6i3AUKJ-bRep6DrfEhOkOoiC9uGv1uFalzVxBelUushlfeWTRQFQsu2eg6Llo2fEkhmTMpEG4BNyNhLeYlCDlrifX7fxbOWsw"
VK_GROUP_ID = 238447439  # цифры

API_VERSION = "5.199"

def send_message(peer_id, text, keyboard=None):
    url = "https://api.vk.com/method/messages.send"
    payload = {
        "access_token": VK_GROUP_TOKEN,
        "v": API_VERSION,
        "peer_id": peer_id,
        "message": text,
        "random_id": 0
    }
    if keyboard:
        payload["keyboard"] = json.dumps(keyboard)
    requests.post(url, data=payload)

def get_keyboard():
    return {
        "one_time": False,
        "buttons": [
            [{"action": {"type": "text", "label": "📦 Заказать"}, "color": "positive"}],
            [{"action": {"type": "text", "label": "💰 Цена"}, "color": "secondary"}],
            [{"action": {"type": "text", "label": "📋 Мои заказы"}, "color": "default"}],
            [{"action": {"type": "text", "label": "ℹ️ Данные"}, "color": "secondary"}]
        ]
    }

print("Бот запущен и слушает Long Poll...")

# Получаем Long Poll сервер
server_url = None
key = None
ts = None

while True:
    if not server_url:
        # Получаем параметры Long Poll
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

    # Запрос к Long Poll
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
            if text == "/start":
                send_message(peer_id, "Привет! Я бот доставки.", keyboard=get_keyboard())
            elif text == "💰 Цена":
                send_message(peer_id, "Тарифы: по городу от 500₽, межгород от 35₽/км")
            elif text == "📦 Заказать":
                send_message(peer_id, "🚧 Заказы скоро появятся!")
            elif text == "📋 Мои заказы":
                send_message(peer_id, "У вас пока нет заказов.")
            elif text == "ℹ️ Данные":
                send_message(peer_id, "Вы не зарегистрированы. Скоро добавим регистрацию.")
            else:
                send_message(peer_id, "Используйте кнопки меню.", keyboard=get_keyboard())






