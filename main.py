import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация (значения берутся из переменных окружения Railway)
BOT_TOKEN = os.environ['BOT_TOKEN']
PORT = int(os.environ.get('PORT', 8000))  # Railway автоматически назначает порт
WEBHOOK_HOST = os.environ.get('RAILWAY_STATIC_URL', '')  # Ваш домен на Railway
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Платежные реквизиты (можно вынести в переменные окружения)
TEAM_ARTICLE_URL = "https://telegra.ph/Your-Team-Article-12-31"
USDT_PAYMENT_LINK = "https://cryptobot.url/your_usdt_link"
XMR_ADDRESS = "84abc123..."
XMR_AMOUNT = "0.19638"
DEPOSIT_AMOUNT = "$49"

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ===================== КЛАВИАТУРЫ =====================
def main_menu_kb():
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton("О тиме", callback_data="about_team"),
        InlineKeyboardButton("Вступить в тиму", callback_data="join_team")
    )

def payment_methods_kb():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("Оплата картой", callback_data="card_payment"),
        InlineKeyboardButton("USDT (Cryptobot)", callback_data="usdt_payment"),
        InlineKeyboardButton("XMR (Monero)", callback_data="xmr_payment"),
        InlineKeyboardButton("Зачем нужен залог", callback_data="why_deposit"),
        InlineKeyboardButton("Назад", callback_data="back_to_main")
    )

def back_kb(target):
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("Назад", callback_data=target)
    )

# ===================== ОБРАБОТЧИКИ КОМАНД =====================
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    try:
        await message.answer_photo(
            types.InputFile('image.jpg'),
            caption="Добро пожаловать в Money Montana!\nВыберите действие:",
            reply_markup=main_menu_kb()
        )
    except Exception as e:
        logger.error(f"Error sending photo: {e}")
        await message.answer(
            "Добро пожаловать в Money Montana!\nВыберите действие:",
            reply_markup=main_menu_kb()
        )

@dp.callback_query_handler(lambda c: c.data == 'about_team')
async def about_team(callback: types.CallbackQuery):
    await callback.answer()
    await bot.send_message(
        callback.from_user.id,
        f"📚 Подробнее о нашей команде:\n{TEAM_ARTICLE_URL}",
        disable_web_page_preview=True
    )

@dp.callback_query_handler(lambda c: c.data == 'join_team')
async def join_team(callback: types.CallbackQuery):
    await callback.answer()
    await bot.send_message(
        callback.from_user.id,
        f"💰 Вступление в тиму Money Montana\n\nДля прохода в тиму необходимо внести залог в размере {DEPOSIT_AMOUNT}\nВыберите способ оплаты:",
        reply_markup=payment_methods_kb()
    )

@dp.callback_query_handler(lambda c: c.data == 'card_payment')
async def card_payment(callback: types.CallbackQuery):
    await callback.answer()
    await bot.send_message(
        callback.from_user.id,
        "⚠️ Оплата картой временно недоступна",
        reply_markup=back_kb("back_to_payment")
    )

@dp.callback_query_handler(lambda c: c.data == 'usdt_payment')
async def usdt_payment(callback: types.CallbackQuery):
    await callback.answer()
    await bot.send_message(
        callback.from_user.id,
        f"💸 Оплата через USDT:\n\n1. Перейдите по ссылке: {USDT_PAYMENT_LINK}\n2. Оплатите счет\n3. Пришлите скриншот оплаты",
        reply_markup=back_kb("back_to_payment")
    )

@dp.callback_query_handler(lambda c: c.data == 'xmr_payment')
async def xmr_payment(callback: types.CallbackQuery):
    await callback.answer()
    await bot.send_message(
        callback.from_user.id,
        f"🔐 Оплата через Monero:\n\nОтправьте СТРОГО {XMR_AMOUNT} XMR на адрес:\n\n<code>{XMR_ADDRESS}</code>\n\nПосле оплаты пришлите txid транзакции",
        parse_mode="HTML",
        reply_markup=back_kb("back_to_payment")
    )

@dp.callback_query_handler(lambda c: c.data == 'why_deposit')
async def why_deposit(callback: types.CallbackQuery):
    await callback.answer()
    await bot.send_message(
        callback.from_user.id,
        "🔒 Залог нужен для:\n\n• Подтверждения серьезности намерений\n• Защиты сообщества от мошенников\n• Доступа к закрытым материалам\n\nЗалог возвращается при выходе из тимы.",
        reply_markup=back_kb("back_to_payment")
    )

@dp.callback_query_handler(lambda c: c.data.startswith('back_'))
async def back_handler(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    
    if callback.data == 'back_to_main':
        await send_welcome(callback.message)
    elif callback.data == 'back_to_payment':
        await join_team(callback)

# ===================== WEBHOOK SETUP =====================
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Bot started. Webhook URL: {WEBHOOK_URL}")

async def handle_webhook(request):
    update = await request.json()
    update = types.Update(**update)
    await dp.process_update(update)
    return web.Response()

app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle_webhook)
app.on_startup.append(on_startup)

def run_app():
    web.run_app(app, host='0.0.0.0', port=PORT)

if __name__ == '__main__':
    run_app()
