import sqlite3
import telebot
from telebot import types



conn = sqlite3.connect('shop.db', check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы продуктов, если она не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL
)
''')

# Создание таблицы клиентов, если она не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER UNIQUE,
    name TEXT,
    purchase_history TEXT
)
''')

# Заполнение таблицы продуктов начальными данными, если она пуста
cursor.execute('SELECT COUNT(*) FROM products')
if cursor.fetchone()[0] == 0:
    products = [('Товар 1', 10), ('Товар 2', 20),
                ('Товар 3', 15), ('Товар 4', 5)]
    cursor.executemany(
        'INSERT INTO products (name, quantity) VALUES (?, ?)', products)
    conn.commit()

# Токен, полученный от BotFather
bot = telebot.TeleBot('7010261764:AAFT655HTcZcPWPZHG4oTTgV77rSsZ30nf8')

# Отправка приветственного сообщения и отображение товаров


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Добро пожаловать в наш магазин!")
    show_products(message)


def show_products(message):
    cursor.execute('SELECT name, quantity FROM products')
    products = cursor.fetchall()
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for product in products:
        product_button = types.KeyboardButton(
            f'{product[0]} (Доступно: {product[1]})')
        markup.add(product_button)
    back_button = types.KeyboardButton('Назад')
    markup.add(back_button)
    bot.send_message(message.chat.id, "Выберите товар:", reply_markup=markup)


@bot.message_handler(func=lambda message: 'Доступно:' in message.text)
def handle_product_selection(message):
    product_name = message.text.split(' (')[0]
    cursor.execute(
        'SELECT quantity FROM products WHERE name = ?', (product_name,))
    quantity = cursor.fetchone()[0]
    if quantity > 0:
        cursor.execute(
            'UPDATE products SET quantity = quantity - 1 WHERE name = ?', (product_name,))
        conn.commit()
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        pay_button = types.KeyboardButton('Оплатить')
        back_button = types.KeyboardButton('Назад')
        markup.add(pay_button, back_button)
        bot.send_message(message.chat.id, f"Вы выбрали {
                         product_name}. Пожалуйста, выберите способ оплаты.", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Извините, этот товар закончился.")
        show_products(message)


@bot.message_handler(func=lambda message: message.text == 'Оплатить')
def handle_payment(message):
    bot.send_message(
        message.chat.id, "Оплата прошла успешно! Спасибо за покупку.")
    show_products(message)


@bot.message_handler(func=lambda message: message.text == 'Назад')
def handle_back(message):
    show_products(message)


# Запуск бота
while True: 
    try:
        bot.polling(non_stop=True)
    except:
        continue