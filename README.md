# **Политбот**

**Политбот** — это **Telegram-бот**, который классифицирует текст, определяя, связан ли он с **политикой**. Бот использует модель **zero-shot классификации** с помощью библиотеки **Hugging Face Transformers**.

## 🚀 **Установка и настройка**

Следуйте этим шагам, чтобы настроить и запустить **Политбота**:

### **1. Клонирование репозитория**

```sh
git clone https://github.com/GoodchildTrevor/polit_classification_bot.git
```
### **2. Установка зависимостей**

```sh
pip install -r requirements.txt
```
### **3. Установка зависимостей**
Создайте файл .env в корневом каталоге и добавьте ваш Telegram API токен:
```sh
TELEGRAM_TOKEN=your_telegram_token_here
```
### **4. Запуск**
Запустите бота с помощью следующей команды:
```sh
python bot.py
```

## 💬 **Использование**
- Начните чат с ботом, отправив команду /start.
- Нажмите на кнопку "Попробовать" для начала взаимодействия.
- Введите текст, который хотите классифицировать.
- Получите результат классификации с вероятностью принадлежности текста к теме политики.
- Чтобы классифицировать другой текст, нажмите на соответствующую кнопку и повторите процесс.

