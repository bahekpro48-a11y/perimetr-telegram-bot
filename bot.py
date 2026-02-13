# -*- coding: utf-8 -*-
import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram.constants import ParseMode

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация из переменных окружения
TOKEN = os.getenv('BOT_TOKEN', '8513311228:AAGVmEqSAMI0suvKdPrArQskLw9uzsT25A0')
CHANNEL_ID = os.getenv('CHANNEL_ID', '@perimetr24msk')
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '0')) if os.getenv('ADMIN_USER_ID') else None

# Состояния
WAITING_CONFIRMATION = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    global ADMIN_USER_ID
    
    user = update.effective_user
    
    # Сохраняем ID первого пользователя как админа
    if not ADMIN_USER_ID:
        ADMIN_USER_ID = user.id
        logger.info(f"Admin user set: {user.id} ({user.first_name})")
    
    keyboard = [[KeyboardButton("ℹ️ Помощь")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        "🤖 Я бот для публикации в канал «Периметр».\n\n"
        "📝 Просто отправь мне:\n"
        "• Текст для публикации\n"
        "• Фото с подписью\n"
        "• Видео с подписью\n\n"
        "✨ Я опубликую это в канале!",
        reply_markup=reply_markup
    )
    logger.info(f"Start command from {user.first_name} (ID: {user.id})")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текста"""
    user_id = update.effective_user.id
    
    if ADMIN_USER_ID and user_id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ Нет доступа")
        logger.warning(f"Unauthorized access attempt from {user_id}")
        return
    
    text = update.message.text
    
    if text in ["ℹ️ Помощь"]:
        await update.message.reply_text(
            "📖 <b>Инструкция:</b>\n\n"
            "1. Отправьте текст — я опубликую его в канале\n"
            "2. Отправьте фото с подписью — я опубликую фото\n"
            "3. Отправьте видео — я опубликую видео\n\n"
            "✅ Всё происходит автоматически!\n\n"
            "📱 Канал: @perimetr24msk",
            parse_mode=ParseMode.HTML
        )
        return
    
    context.user_data['pending_text'] = text
    
    keyboard = [[KeyboardButton("✅ Опубликовать"), KeyboardButton("❌ Отменить")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    preview = text[:300] + "..." if len(text) > 300 else text
    
    await update.message.reply_text(
        f"📋 <b>
