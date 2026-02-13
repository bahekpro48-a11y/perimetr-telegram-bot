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

# Конфигурация
TOKEN = os.getenv('BOT_TOKEN', '8513311228:AAGVmEqSAMI0suvKdPrArQskLw9uzsT25A0')
CHANNEL_ID = os.getenv('CHANNEL_ID', '@perimetr24msk')
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '0')) if os.getenv('ADMIN_USER_ID') else None

# Состояния
WAITING_CONFIRMATION = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    global ADMIN_USER_ID
    
    user = update.effective_user
    
    if not ADMIN_USER_ID:
        ADMIN_USER_ID = user.id
        logger.info(f"Admin user set: {user.id} ({user.first_name})")
    
    keyboard = [[KeyboardButton("ℹ️ Помощь")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    message_text = (
        f"👋 Привет, {user.first_name}!\n\n"
        "🤖 Я бот для публикации в канал «Периметр».\n\n"
        "📝 Просто отправь мне:\n"
        "• Текст для публикации\n"
        "• Фото с подписью\n"
        "• Видео с подписью\n\n"
        "✨ Я опубликую это в канале!"
    )
    
    await update.message.reply_text(message_text, reply_markup=reply_markup)
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
        help_text = (
            "📖 <b>Инструкция:</b>\n\n"
            "1. Отправьте текст — я опубликую его в канале\n"
            "2. Отправьте фото с подписью — я опубликую фото\n"
            "3. Отправьте видео — я опубликую видео\n\n"
            "✅ Всё происходит автоматически!\n\n"
            "📱 Канал: @perimetr24msk"
        )
        await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)
        return
    
    context.user_data['pending_text'] = text
    
    keyboard = [[KeyboardButton("✅ Опубликовать"), KeyboardButton("❌ Отменить")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    preview = text[:300] + "..." if len(text) > 300 else text
    message_text = f"📋 <b>Предпросмотр:</b>\n\n{preview}\n\nОпубликовать в канале?"
    
    await update.message.reply_text(
        message_text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    
    return WAITING_CONFIRMATION

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка фото"""
    user_id = update.effective_user.id
    
    if ADMIN_USER_ID and user_id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ Нет доступа")
        return
    
    photo = update.message.photo[-1]
    caption = update.message.caption or ""
    
    context.user_data['pending_photo'] = photo.file_id
    context.user_data['pending_caption'] = caption
    
    keyboard = [[KeyboardButton("✅ Опубликовать"), KeyboardButton("❌ Отменить")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    caption_preview = caption[:100] if caption else '[нет]'
    message_text = (
        f"📸 <b>Фото получено!</b>\n\n"
        f"Подпись: {caption_preview}\n\n"
        "Опубликовать в канале?"
    )
    
    await update.message.reply_text(
        message_text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    
    return WAITING_CONFIRMATION

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка видео"""
    user_id = update.effective_user.id
    
    if ADMIN_USER_ID and user_id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ Нет доступа")
        return
    
    video = update.message.video
    caption = update.message.caption or ""
    
    context.user_data['pending_video'] = video.file_id
    context.user_data['pending_caption'] = caption
    
    keyboard = [[KeyboardButton("✅ Опубликовать"), KeyboardButton("❌ Отменить")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    caption_preview = caption[:100] if caption else '[нет]'
    message_text = (
        f"🎥 <b>Видео получено!</b>\n\n"
        f"Подпись: {caption_preview}\n\n"
        "Опубликовать в канале?"
    )
    
    await update.message.reply_text(
        message_text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    
    return WAITING_CONFIRMATION

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение публикации"""
    text = update.message.text
    
    if text == "✅ Опубликовать":
        try:
            if 'pending_text' in context.user_data:
                await context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=context.user_data['pending_text'],
                    parse_mode=ParseMode.HTML
                )
                await update.message.reply_text("✅ Текст опубликован в канале!", reply_markup=ReplyKeyboardRemove())
                logger.info("Text published to channel")
            
            elif 'pending_photo' in context.user_data:
                await context.bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=context.user_data['pending_photo'],
                    caption=context.user_data.get('pending_caption', ''),
                    parse_mode=ParseMode.HTML
                )
                await update.message.reply_text("✅ Фото опубликовано в канале!", reply_markup=ReplyKeyboardRemove())
                logger.info("Photo published to channel")
            
            elif 'pending_video' in context.user_data:
                await context.bot.send_video(
                    chat_id=CHANNEL_ID,
                    video=context.user_data['pending_video'],
                    caption=context.user_data.get('pending_caption', ''),
                    parse_mode=ParseMode.HTML
                )
                await update.message.reply_text("✅ Видео опубликовано в канале!", reply_markup=ReplyKeyboardRemove())
                logger.info("Video published to channel")
        
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка публикации: {e}", reply_markup=ReplyKeyboardRemove())
            logger.error(f"Publication error: {e}")
    
    elif text == "❌ Отменить":
        await update.message.reply_text("❌ Публикация отменена", reply_markup=ReplyKeyboardRemove())
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена"""
    context.user_data.clear()
    await update.message.reply_text("❌ Отменено", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    """Запуск бота"""
    logger.info("="*60)
    logger.info("🚀 Starting Perimetr Telegram Bot...")
    logger.info(f"Channel ID: {CHANNEL_ID}")
    logger.info("="*60)
    
    application = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text),
            MessageHandler(filters.PHOTO, handle_photo),
            MessageHandler(filters.VIDEO, handle_video)
        ],
        states={
            WAITING_CONFIRMATION: [MessageHandler(filters.TEXT, confirm)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(conv_handler)
    
    logger.info("✅ Bot started successfully!")
    logger.info("📱 Send /start to @perimetr_poster_bot")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
