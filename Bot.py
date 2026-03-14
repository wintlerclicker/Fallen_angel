#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FALLEN ANGEL - TELEGRAM БОТ ДЛЯ BOTHOST
Работает с API твоего сайта
"""

import os
import sys
import requests
import json
import time
import threading
import logging
from datetime import datetime
import telebot

# =============== НАСТРОЙКА ЛОГИРОВАНИЯ ===============
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# =============== ТВОИ ДАННЫЕ ===============
BOT_TOKEN = '8034708016:AAFKAguLy8pvWdGgya7O_Utj0NwogpVuFbQ'
ADMIN_ID = '8537481169'
SITE_URL = 'https://xerodon.pythonanywhere.com'
API_KEY = 'FallenAngelSecretKey2026'

# Создаем бота
bot = telebot.TeleBot(BOT_TOKEN)

# Файл для хранения отправленных ID
SENT_FILE = 'sent_ids.json'

def load_sent():
    """Загружает список отправленных ID"""
    if os.path.exists(SENT_FILE):
        try:
            with open(SENT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'projects': [], 'requests': []}
    return {'projects': [], 'requests': []}

def save_sent(sent):
    """Сохраняет список отправленных ID"""
    try:
        with open(SENT_FILE, 'w', encoding='utf-8') as f:
            json.dump(sent, f, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения: {e}")

# =============== ЗАПРОСЫ К ТВОЕМУ САЙТУ ===============
def api_request(endpoint, params=None):
    """Универсальная функция для запросов к API"""
    try:
        url = f"{SITE_URL}{endpoint}"
        
        if params is None:
            params = {}
        params['key'] = API_KEY
        
        logger.info(f"Запрос к {url}")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Ошибка API {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Ошибка запроса: {e}")
        return None

def get_new_projects(last_ids=None):
    """Получает новые проекты с сайта"""
    params = {}
    if last_ids:
        params['last_ids'] = ','.join(str(x) for x in last_ids)
    
    data = api_request('/api/bot/new_projects/', params)
    if data and 'projects' in data:
        return data['projects']
    return []

def get_new_requests(last_ids=None):
    """Получает новые заявки с сайта"""
    params = {}
    if last_ids:
        params['last_ids'] = ','.join(str(x) for x in last_ids)
    
    data = api_request('/api/bot/new_requests/', params)
    if data and 'requests' in data:
        return data['requests']
    return []

def get_stats():
    """Получает статистику с сайта"""
    data = api_request('/api/bot/stats/')
    return data if data else None

# =============== КОМАНДЫ БОТА ===============
@bot.message_handler(commands=['start'])
def start(message):
    """Команда /start"""
    user = message.from_user
    bot.reply_to(
        message, 
        f"👋 Привет, {user.first_name}!\n\n"
        f"Я бот Fallen Angel. Я присылаю уведомления о новых проектах и заявках.\n\n"
        f"📋 Команды:\n"
        f"/stats - статистика сайта\n"
        f"/projects - последние проекты\n"
        f"/requests - последние заявки\n"
        f"/help - помощь\n\n"
        f"🌐 Сайт: {SITE_URL}"
    )
    logger.info(f"Пользователь {user.id} запустил бота")

@bot.message_handler(commands=['help'])
def help_command(message):
    """Команда /help"""
    bot.reply_to(
        message,
        "📋 ПОМОЩЬ\n\n"
        "Команды:\n"
        "/start - начало работы\n"
        "/stats - статистика сайта\n"
        "/projects - последние проекты\n"
        "/requests - последние заявки\n"
        "/help - это сообщение\n\n"
        "Уведомления:\n"
        "Бот автоматически присылает уведомления о:\n"
        "• Новых проектах\n"
        "• Новых заявках в поддержку\n\n"
        f"🌐 Сайт: {SITE_URL}\n"
        f"🔐 Админка: {SITE_URL}/admin"
    )

@bot.message_handler(commands=['stats'])
def stats(message):
    """Команда /stats - статистика"""
    stats_data = get_stats()
    
    if stats_data:
        text = (
            "📊 СТАТИСТИКА САЙТА\n\n"
            f"📁 Всего проектов: {stats_data['total_projects']}\n"
            f"📨 Всего заявок: {stats_data['total_requests']}\n\n"
            f"📅 За сегодня:\n"
            f"   • Новых проектов: {stats_data['new_projects_today']}\n"
            f"   • Новых заявок: {stats_data['new_requests_today']}"
        )
    else:
        text = "❌ Не удалось получить статистику. Проверь подключение к сайту."
    
    bot.reply_to(message, text)

@bot.message_handler(commands=['projects'])
def projects(message):
    """Команда /projects - последние проекты"""
    projects_data = get_new_projects()
    
    if not projects_data:
        bot.reply_to(message, "📁 Проектов пока нет")
        return
    
    text = "📁 ПОСЛЕДНИЕ ПРОЕКТЫ\n\n"
    for p in projects_data[:5]:
        text += f"• {p['name']}\n"
        text += f"  👤 {p['user']}\n"
        text += f"  📊 {p['status']}\n\n"
    
    bot.reply_to(message, text)

@bot.message_handler(commands=['requests'])
def requests_cmd(message):
    """Команда /requests - последние заявки"""
    requests_data = get_new_requests()
    
    if not requests_data:
        bot.reply_to(message, "📨 Заявок пока нет")
        return
    
    text = "📨 ПОСЛЕДНИЕ ЗАЯВКИ\n\n"
    for r in requests_data[:5]:
        text += f"• {r['subject']}\n"
        text += f"  👤 {r['user']}\n"
        text += f"  📊 {r['status']}\n\n"
    
    bot.reply_to(message, text)

# =============== ФОНОВАЯ ПРОВЕРКА ===============
def check_updates():
    """Проверка новых данных (в отдельном потоке)"""
    logger.info("🟢 Запуск проверки")
    
    while True:
        try:
            sent = load_sent()
            new_sent = False
            
            # Проверяем проекты
            projects = get_new_projects(sent['projects'])
            for p in projects:
                if p['id'] not in sent['projects']:
                    logger.info(f"Новый проект #{p['id']}")
                    
                    # Создаем клавиатуру с кнопкой
                    keyboard = telebot.types.InlineKeyboardMarkup()
                    button = telebot.types.InlineKeyboardButton(
                        text="👁 Посмотреть",
                        url=f"{SITE_URL}{p['url']}"
                    )
                    keyboard.add(button)
                    
                    text = (
                        f"🆕 НОВЫЙ ПРОЕКТ!\n\n"
                        f"📁 Название: {p['name']}\n"
                        f"👤 Клиент: {p['user']}\n"
                        f"📊 Статус: {p['status']}"
                    )
                    
                    bot.send_message(ADMIN_ID, text, reply_markup=keyboard)
                    sent['projects'].append(p['id'])
                    new_sent = True
            
            # Проверяем заявки
            requests_data = get_new_requests(sent['requests'])
            for r in requests_data:
                if r['id'] not in sent['requests']:
                    logger.info(f"Новая заявка #{r['id']}")
                    
                    # Создаем клавиатуру с кнопкой
                    keyboard = telebot.types.InlineKeyboardMarkup()
                    button = telebot.types.InlineKeyboardButton(
                        text="👁 Посмотреть",
                        url=f"{SITE_URL}{r['url']}"
                    )
                    keyboard.add(button)
                    
                    text = (
                        f"📨 НОВАЯ ЗАЯВКА!\n\n"
                        f"📌 Тема: {r['subject']}\n"
                        f"👤 Клиент: {r['user']}\n"
                        f"📊 Статус: {r['status']}"
                    )
                    
                    bot.send_message(ADMIN_ID, text, reply_markup=keyboard)
                    sent['requests'].append(r['id'])
                    new_sent = True
            
            if new_sent:
                save_sent(sent)
                logger.info(f"💾 Сохранено. Проектов: {len(sent['projects'])}, Заявок: {len(sent['requests'])}")
            
            time.sleep(30)  # Проверка каждые 30 секунд
            
        except Exception as e:
            logger.error(f"❌ Ошибка в фоновом потоке: {e}")
            time.sleep(60)

# =============== ЗАПУСК ===============
if __name__ == "__main__":
    print("="*60)
    print("🤖 FALLEN ANGEL TELEGRAM BOT for BOTHOST")
    print("="*60)
    print(f"📱 Токен: {BOT_TOKEN[:10]}...{BOT_TOKEN[-10:]}")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print(f"🌐 Сайт: {SITE_URL}")
    print(f"🔑 API Key: {API_KEY}")
    print("="*60)
    
    # Проверка API
    print("🔄 Проверка подключения к API...")
    test = get_stats()
    if test is not None:
        print("✅ API работает!")
        print(f"📊 Статистика: {test}")
    else:
        print("⚠️ API не отвечает. Проверь настройки.")
    
    # Запускаем фоновую проверку
    thread = threading.Thread(target=check_updates, daemon=True)
    thread.start()
    
    print("✅ Бот запущен и готов к работе!")
    print("📨 Ожидание новых проектов и заявок...")
    print("="*60)
    print("Бот работает 24/7 на Bothost!")
    print("="*60)
    
    # Запускаем бота (эта строка не даст скрипту завершиться)
    bot.infinity_polling()
