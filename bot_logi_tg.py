import telebot
import random
import logging
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('heizung_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Мультиязычная база знаний
KNOWLEDGE_BASE = {
    'german': {
        'problem': {
            'keywords': ['heizung', 'warm', 'kalt', 'geht nicht', 'funktioniert', 'problem', 'störung'],
            'responses': [
                "Bei Heizungsproblemen: Ist die Heizung komplett kalt oder wird sie nicht richtig warm?",
                "Prüfen Sie zunächst den Thermostat und ob die Heizung Strom hat. Beschreiben Sie das Problem genauer.",
                "Typische Probleme: Keine Wärme, seltsame Geräusche oder Druckverlust. Was genau beobachten Sie?"
            ]
        },
        'repair': {
            'keywords': ['reparatur', 'reparieren', 'kaputt', 'defekt', 'techniker'],
            'responses': [
                "Reparaturkosten: Einfache Reparaturen ab 80€, komplexere nach Aufwand.",
                "Unsere zertifizierten Techniker kommen innerhalb von 24 Stunden."
            ]
        },
        'cost': {
            'keywords': ['kosten', 'preis', 'teuer', 'günstig', 'angebot'],
            'responses': [
                "Gasheizung Neuinstallation: ab 5.000€ inkl. Montage",
                "Wärmepumpe: ab 12.000€ (bis zu 35% Förderung möglich)"
            ]
        },
        'emergency': {
            'keywords': ['notfall', 'notdienst', 'dringend', 'sofort'],
            'responses': [
                "🚨 NOTDIENST: 0800-HEIZUNG-NOT\nTechniker innerhalb von 2 Stunden vor Ort!"
            ]
        },
        'greeting': {
            'keywords': ['hallo', 'guten tag', 'hi', 'moin'],
            'responses': [
                "Guten Tag! Ich bin Ihr Heizungsberater von Germany Heizung. Wie kann ich helfen?"
            ]
        }
    },
    'russian': {
        'problem': {
            'keywords': ['отопление', 'тепло', 'холодно', 'не работает', 'проблема', 'сломал', 'не греет'],
            'responses': [
                "При проблемах с отоплением: Батареи полностью холодные или плохо греют?",
                "Проверьте термостат и подачу электричества. Опишите проблему подробнее.",
                "Типичные проблемы: нет тепла, странные звуки или падение давления. Что именно происходит?"
            ]
        },
        'repair': {
            'keywords': ['ремонт', 'починить', 'сломался', 'неисправность', 'техник'],
            'responses': [
                "Стоимость ремонта: простой ремонт от 80€, сложный - по запросу.",
                "Наши сертифицированные техники приедут в течение 24 часов."
            ]
        },
        'cost': {
            'keywords': ['стоимость', 'цена', 'дорого', 'дешево', 'предложение'],
            'responses': [
                "Новая газовая система: от 5.000€ с установкой",
                "Тепловой насос: от 12.000€ (возможна субсидия до 35%)"
            ]
        },
        'emergency': {
            'keywords': ['срочно', 'авария', 'аварийный', 'немедленно', 'прорвало'],
            'responses': [
                "🚨 АВАРИЙНАЯ СЛУЖБА: 0800-HEIZUNG-NOT\nТехник в течение 2 часов!"
            ]
        },
        'greeting': {
            'keywords': ['привет', 'здравствуйте', 'добрый день', 'здравствуй'],
            'responses': [
                "Здравствуйте! Я ваш консультант по отоплению Germany Heizung. Чем могу помочь?"
            ]
        }
    }
}

# Статистика пользователей
user_stats = {}
ADMIN_ID = 901595460  # Ваш ID


def detect_language(message):
    """Определяет язык сообщения"""
    russian_chars = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
    text = message.lower()

    ru_count = sum(1 for char in text if char in russian_chars)

    if ru_count > 0:
        return 'russian'
    else:
        return 'german'


def get_response(message, language):
    """Получает ответ на соответствующем языке"""
    lower_msg = message.lower()
    knowledge = KNOWLEDGE_BASE[language]

    for category, data in knowledge.items():
        for keyword in data['keywords']:
            if keyword in lower_msg:
                return random.choice(data['responses'])

    default_responses = {
        'german': "Ich verstehe Ihr Anliegen. Könnten Sie es genauer beschreiben?",
        'russian': "Я понял ваш вопрос. Не могли бы вы описать подробнее?"
    }

    return default_responses[language]


def log_message(user, message):
    """Логирует сообщение пользователя"""
    username = f"@{user.username}" if user.username else "No username"
    log_entry = f"👤 {user.first_name} ({username}) | 💬 {message}"
    logging.info(log_entry)
    print(f"📨 {log_entry}")


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user = message.from_user
    log_message(user, f"/start command")

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        "🔧 Problem/Проблема",
        "💶 Kosten/Стоимость",
        "🚨 Notdienst/Авария",
        "📞 Kontakt/Контакты"
    ]
    keyboard.add(*buttons)

    welcome_text = """
🔥 Germany Heizung 🔥

Язык/Language: DE / RU

Просто напишите вопрос!
Schreiben Sie Ihre Frage!
    """
    bot.send_message(message.chat.id, welcome_text, reply_markup=keyboard)


@bot.message_handler(commands=['stats'])
def show_stats(message):
    """Показывает статистику (только для админа)"""
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔ Nur für Administrator")
        return

    if not user_stats:
        bot.send_message(message.chat.id, "📊 Noch keine Statistiken")
        return

    stats_text = "📊 Bot-Statistiken:\n\n"
    for user_id, data in user_stats.items():
        stats_text += f"👤 {data['first_name']}\n"
        stats_text += f"📨 Nachrichten: {data['message_count']}\n"
        stats_text += f"🕐 Zuletzt: {data['last_seen']}\n"
        stats_text += "─" * 20 + "\n"

    bot.send_message(message.chat.id, stats_text)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user = message.from_user
    user_message = message.text

    # Логируем сообщение
    log_message(user, user_message)

    # Обновляем статистику
    user_id = user.id
    if user_id not in user_stats:
        user_stats[user_id] = {
            'first_name': user.first_name,
            'username': user.username,
            'message_count': 0,
            'last_seen': datetime.now().strftime("%H:%M:%S")
        }

    user_stats[user_id]['message_count'] += 1
    user_stats[user_id]['last_seen'] = datetime.now().strftime("%H:%M:%S")

    # Обрабатываем сообщение
    language = detect_language(user_message)
    response = get_response(user_message, language)
    bot.send_message(message.chat.id, response)


if __name__ == "__main__":
    print("🤖 Бот запущен с логированием!")
    print("📝 Логи сохраняются в heizung_bot.log")
    print("📊 Статистика: /stats (только для админа)")
    bot.infinity_polling()