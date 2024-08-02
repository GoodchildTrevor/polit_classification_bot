from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters)

from transformers import pipeline

classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
candidate_labels = ["politics", "economy", "entertainment", "environment"]

from dotenv import load_dotenv
import os

load_dotenv()

telegram_token = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Попробовать", callback_data='start_interaction')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Добро пожаловать в Политбот. Нажмите кнопку ниже, чтобы начать.', reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['ready_for_classification'] = True
    await query.edit_message_text(text="Теперь введите текст для классификации.")


async def classification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text and not update.message.text.startswith('/'):
        if context.user_data.get('ready_for_classification', False):
            sequence_to_classify = update.message.text
            polit_topic = classifier(sequence_to_classify, candidate_labels, multi_label=False)
            index_of_politics = polit_topic['labels'].index('politics')
            politics = 'политика' if index_of_politics == 0 else 'не политика'
            politics_score = polit_topic['scores'][index_of_politics]
            await update.message.reply_text(f'Это {politics}. Политика с вероятностью {politics_score*100:.2f}%')
            # После отправки классификации устанавливаем флаг готовности к новой классификации
            context.user_data['ready_for_classification'] = False

            # Отправляем кнопку для нового запроса
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


app = ApplicationBuilder().token(f"{telegram_token}").build()

app.add_handler(CommandHandler('start', start))

# Обработчик для кнопок
app.add_handler(CallbackQueryHandler(button))

# Обработчик для всех текстовых сообщений
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, callback=classification))

app.run_polling()