from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters)

from transformers import pipeline

from dotenv import load_dotenv
import os

import warnings

warnings.filterwarnings('ignore')

# Загружаем модель для zero-shot классификации с использованием Hugging Face Transformers
classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
candidate_labels = ["politics", "economy", "entertainment", "environment"]

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем токен для Telegram бота из переменных окружения
telegram_token = os.getenv("TELEGRAM_TOKEN")

# Функция, которая будет вызываться при вводе команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Создаем кнопку для начала взаимодействия
    keyboard = [
        [InlineKeyboardButton("Попробовать", callback_data='start_interaction')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Добро пожаловать в Политбот. Нажмите кнопку ниже, чтобы начать.', reply_markup=reply_markup)

# Функция-обработчик нажатия на кнопку
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # Устанавливаем флаг готовности к классификации текста
    context.user_data['ready_for_classification'] = True
    await query.edit_message_text(text="Теперь введите текст для классификации.")

# Функция для классификации текста, введенного пользователем
async def classification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text and not update.message.text.startswith('/'):
        if context.user_data.get('ready_for_classification', False):
            sequence_to_classify = update.message.text
            # Классифицируем текст с использованием модели
            polit_topic = classifier(sequence_to_classify, candidate_labels, multi_label=False)
            index_of_politics = polit_topic['labels'].index('politics')
            politics = 'политика' if index_of_politics == 0 else 'не политика'
            politics_score = polit_topic['scores'][index_of_politics]
            # Отправляем пользователю результат классификации
            await update.message.reply_text(f'Это {politics}. Политика с вероятностью {politics_score*100:.2f}%')
            # Сбрасываем флаг готовности к новой классификации
            context.user_data['ready_for_classification'] = False

            # Создаем кнопку для нового запроса классификации
            keyboard = [
                [InlineKeyboardButton("Классифицировать другой текст", callback_data='start_interaction')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Нажмите кнопку ниже, чтобы начать новую классификацию.", reply_markup=reply_markup)
        else:
            # Если флаг не установлен, предлагаем пользователю начать классификацию
            keyboard = [
                [InlineKeyboardButton("Попробовать", callback_data='start_interaction')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Нажмите кнопку ниже, чтобы начать классификацию текста.", reply_markup=reply_markup)

# Создаем экземпляр приложения Telegram
app = ApplicationBuilder().token(f"{telegram_token}").build()

# Добавляем обработчик для команды /start
app.add_handler(CommandHandler('start', start))

# Добавляем обработчик для нажатия на кнопки
app.add_handler(CallbackQueryHandler(button))

# Добавляем обработчик для всех текстовых сообщений, кроме команд
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, callback=classification))

# Запускаем бота
app.run_polling()
