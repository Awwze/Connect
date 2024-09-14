import logging
import time
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Определение состояний для ConversationHandler
MAIN_MENU, CATEGORY, GET_PHONE, GET_DETAILS, CONFIRM_ORDER = range(5)

# Корзина пользователя
user_data = {}

# Телеграм пользователя-администратора для уведомлений
admin_chat_id = '-4222268084'  # Замените на ваш chat ID

prices = {
    'Телеграм боты': {
        'Онлайн школа': 'от 35$',
        'Красота': 'от 25$',
        'Кафе': 'от 30$',
        'Telegram miniApps': '10$',
        'Другое': 'зависит от Ваших предпочтений'
    },
    'Веб-сайты': {
        'Онлайн школа': 'от 60$',
        'Красота': 'от 15$',
        'Кафе': 'от 30$',
        'E-commerce': 'от 60$',
        'Другое': 'зависит от Ваших предпочтений'
    },
    'Биты': {
        'Полный бит': '30$'
    },
    'Превью': {
        'YouTube': 'от 10$',
        'TikTok/Instagram': 'от 10$'
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    price_text = '📌 *Добро пожаловать! Выберите раздел:*\n\n'
    for section, items in prices.items():
        price_text += f'*{section}:*\n'
        for item, price in items.items():
            price_text += f'- {item} - {price}\n'
        price_text += '\n'
    
    reply_keyboard = [['🤖 Телеграм боты', '💻 Веб-сайты'], ['🎧 Биты', '🖼 Превью'], ['📌 Заказать', '☎️ Контакты']]
    await update.message.reply_text(
        price_text,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        parse_mode='Markdown'
    )
    return MAIN_MENU

async def bot_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data['section'] = 'Телеграм боты'
    price_text = '📌 *Выберите категорию для Телеграм бота:*\n'
    for category, price in prices['Телеграм боты'].items():
        price_text += f'- {category} - {price}\n'
    
    reply_keyboard = [['📚 Онлайн школа', '💄 Красота'], ['🏪 Кафе', '📱 Telegram miniApps'], ['📝 Другое', '⬅️ Назад']]
    await update.message.reply_text(
        price_text,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        parse_mode='Markdown'
    )
    return CATEGORY

async def website_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data['section'] = 'Веб-сайты'
    price_text = '📌 *Выберите категорию для веб-сайта:*\n'
    for category, price in prices['Веб-сайты'].items():
        price_text += f'- {category} - {price}\n'
    
    reply_keyboard = [['📚 Онлайн школа', '💄 Красота'], ['🏪 Кафе', '💼 Интернет Магазин'], ['📝 Другое', '⬅️ Назад']]
    await update.message.reply_text(
        price_text,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        parse_mode='Markdown'
    )
    return CATEGORY

async def request_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == '⬅️ Назад':
        return await start(update, context)
    user_data['category'] = update.message.text
    await update.message.reply_text(
        '📞 *Пожалуйста, отправьте ваш номер телефона:*',
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("📞 Отправить номер телефона", request_contact=True)], ['⬅️ Назад']], one_time_keyboard=True, resize_keyboard=True),
        parse_mode='Markdown'
    )
    return GET_PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.contact:
        user_data['phone_number'] = update.message.contact.phone_number
        user_data['username'] = update.message.from_user.username
        await update.message.reply_text(
            '✍️ *Спасибо! Теперь опишите, что конкретно вы хотите, и подробнее напишите о вашей компании:*',
            parse_mode='Markdown'
        )
        return GET_DETAILS
    elif update.message.text == 'Назад':
        return await start(update, context)
    else:
        await update.message.reply_text(
            '📞 *Пожалуйста, используйте кнопку ниже для отправки номера телефона:*',
            parse_mode='Markdown'
        )
        return GET_PHONE

async def get_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == 'Назад':
        return await start(update, context)
    user_data['details'] = update.message.text
    await update.message.reply_text(
        '📌 *Спасибо! Нажмите "Отправить", чтобы отправить данные, или "Назад", чтобы вернуться.*',
        reply_markup=ReplyKeyboardMarkup([['Отправить', 'Назад']], one_time_keyboard=True, resize_keyboard=True),
        parse_mode='Markdown'
    )
    return CONFIRM_ORDER

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == 'Отправить':
        order_text = (
            f"Раздел: {user_data.get('section', 'Не указано')}\n"
            f"Категория: {user_data.get('category', 'Не указано')}\n"
            f"Номер телефона: {user_data.get('phone_number', 'Не указано')}\n"
            f"Юзернейм: @{user_data.get('username', 'Не указано')}\n"
            f"Детали: {user_data.get('details', 'Не указано')}"
        )
        await context.bot.send_message(chat_id=admin_chat_id, text=order_text)

        await update.message.reply_text('✅ *Спасибо! Ваши данные отправлены. В скором времени с Вами свяжется администратор.*', parse_mode='Markdown')
        user_data.clear()
        return await start(update, context)
    elif update.message.text == 'Назад':
        return await start(update, context)
    else:
        await update.message.reply_text(
            '📌 *Пожалуйста, выберите "Отправить" или "Назад".*',
            parse_mode='Markdown'
        )
        return CONFIRM_ORDER

async def show_order_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [['🤖 Телеграм боты', '💻 Веб-сайты'], ['🎧 Биты', '🖼 Превью'], ['☎️ Контакты', '⬅️ Назад']]
    await update.message.reply_text(
        '📌 *Выберите раздел:*',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        parse_mode='Markdown'
    )
    return MAIN_MENU

async def show_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contact_info = (
        "📞 *Контакты:*\n"
        "Телефон: +998946000032\n"
        "Telegram: @Hhhoay\n"
        "Telegram 2: @tgAkbarr"
    )
    await update.message.reply_text(contact_info, parse_mode='Markdown')
    return MAIN_MENU

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    price_text = '📌 *Выберите раздел:*\n\n'
    for section, items in prices.items():
        price_text += f'*{section}:*\n'
        for item, price in items.items():
            price_text += f'- {item} - {price}\n'
        price_text += '\n'
    
    reply_keyboard = [['🤖 Телеграм боты', '💻 Веб-сайты'], ['🎧 Биты', '🖼 Превью'], ['📌 Заказать', '☎️ Контакты']]
    await update.message.reply_text(
        price_text,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
        parse_mode='Markdown'
    )
    return MAIN_MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('👋 *До свидания! Надеемся увидеть вас снова.*', reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown')
    return ConversationHandler.END

def run_bot():
    while True:
        try:
            main()
        except Exception as e:
            logging.error(f"Произошла ошибка: {e}")
            time.sleep(5)  # Задержка перед перезапуском

def main() -> None:
    application = Application.builder().token("7373812547:AAGRQkukT5gUMSSApucrKjHjU1lINCLpOr8").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [
                MessageHandler(filters.Regex('^(🤖 Телеграм боты)$'), bot_menu),
                MessageHandler(filters.Regex('^(💻 Веб-сайты)$'), website_menu),
                MessageHandler(filters.Regex('^(🎧 Биты|🖼 Превью)$'), request_contact),
                MessageHandler(filters.Regex('^(☎️ Контакты)$'), show_contacts),
                MessageHandler(filters.Regex('^(📌 Заказать)$'), show_order_menu)
            ],
            CATEGORY: [
                MessageHandler(filters.Regex('^(📚 Онлайн школа|💄 Красота|🏪 Кафе|📱 Telegram miniApps|💼 Интернет Магазин|📝 Другое)$'), request_contact),
                MessageHandler(filters.Regex('^(⬅️ Назад)$'), show_main_menu)
            ],
            GET_PHONE: [
                MessageHandler(filters.CONTACT, get_phone),
                MessageHandler(filters.Regex('^(⬅️ Назад)$'), start)
            ],
            GET_DETAILS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_details),
                MessageHandler(filters.Regex('^(⬅️ Назад)$'), start)
            ],
            CONFIRM_ORDER: [
                MessageHandler(filters.Regex('^(Отправить)$'), confirm_order),
                MessageHandler(filters.Regex('^(⬅️ Назад)$'), start)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    run_bot()

