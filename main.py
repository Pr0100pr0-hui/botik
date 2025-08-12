import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram import F
from aiohttp import web
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.environ['BOT_TOKEN']
PORT = int(os.environ.get('PORT', 8000))
WEBHOOK_HOST = os.environ.get('RAILWAY_STATIC_URL', '')
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Платежные реквизиты
TEAM_ARTICLE_URL = "https://telegra.ph/Your-Team-Article-12-31"
USDT_PAYMENT_LINK = "http://t.me/send?start=IVqGeFH7lnBz"
XMR_ADDRESS = "42ryGdiDRZ1JezVaCqkc8S8yjeo5JTV8xf2eivCqvqgVAeW3EfcXMaJLUZ4nJSm4KT6AwxuWjEeKgQueoXxMm7txCK5hiYi"
XMR_AMOUNT = "0.19638"
DEPOSIT_AMOUNT = "$49"

# Инициализация бота
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

# ===================== КЛАВИАТУРЫ =====================
def main_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="О тиме", callback_data="about_team")
    builder.button(text="Вступить в тиму", callback_data="join_team")
    builder.adjust(1)
    return builder.as_markup()

def payment_methods_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Оплата картой", callback_data="card_payment")
    builder.button(text="USDT (Cryptobot)", callback_data="usdt_payment")
    builder.button(text="XMR (Monero)", callback_data="xmr_payment")
    builder.button(text="Зачем нужен залог", callback_data="why_deposit")
    builder.button(text="Назад", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()

def back_kb(target: str):
    builder = InlineKeyboardBuilder()
    builder.button(text="Назад", callback_data=target)
    return builder.as_markup()

# ===================== ОБРАБОТЧИКИ =====================
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    try:
        await message.answer_photo(
            types.FSInputFile('image.jpg'),
            caption="⭐ Добро пожаловать в Money Montana! ⭐\n\nВыберите действие:",
            reply_markup=main_menu_kb()
        )
    except Exception as e:
        logger.error(f"Error sending photo: {e}")
        await message.answer(
            "⭐ Добро пожаловать в Money Montana! ⭐\n\nВыберите действие:",
            reply_markup=main_menu_kb()
        )

@dp.callback_query(F.data == "about_team")
async def about_team(callback: types.CallbackQuery):
    try:
        await callback.answer()
        await callback.message.answer(
            f"📚 Подробнее о тиме:\n\n{TEAM_ARTICLE_URL}",
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Error in about_team: {e}")

@dp.callback_query(F.data == "join_team")
async def join_team(callback: types.CallbackQuery):
    try:
        await callback.answer()
        await callback.message.answer(
            f"💰 Вступление в тиму Money Montana 💰\n\nДля прохода в тиму необходимо внести залог в размере {DEPOSIT_AMOUNT}\n\nВыберите способ оплаты:",
            reply_markup=payment_methods_kb()
        )
    except Exception as e:
        logger.error(f"Error in join_team: {e}")

@dp.callback_query(F.data == "card_payment")
async def card_payment(callback: types.CallbackQuery):
    try:
        await callback.answer("💳 Оплата картой временно недоступна 💳\n\nВыберите другой способ оплаты", show_alert=True)
        # Альтернатива - отправка нового сообщения
        # await callback.message.answer("⚠️ Оплата картой временно недоступна")
    except Exception as e:
        logger.error(f"Error in card_payment: {e}")

@dp.callback_query(F.data == "usdt_payment")
async def usdt_payment(callback: types.CallbackQuery):
    try:
        await callback.answer()
        await callback.message.edit_text(
            f"💸 Оплата через USDT 💸\n\nОплатите чек через Cryptobot:\n{USDT_PAYMENT_LINK},
            reply_markup=back_kb("back_to_payment")
        )
    except Exception as e:
        logger.error(f"Error in usdt_payment: {e}")
        # Fallback - отправка нового сообщения
        await callback.message.answer("Произошла ошибка, попробуйте ещё раз")

@dp.callback_query(F.data == "xmr_payment")
async def xmr_payment(callback: types.CallbackQuery):
    try:
        await callback.answer()
        await callback.message.edit_text(
            f"🔐 Оплата через Monero 🔐\n\nОтправьте СТРОГО {XMR_AMOUNT} XMR на адрес:\n\n<code>{XMR_ADDRESS}</code>\n\nПроверка оплаты занимает 10-20 мин",
            parse_mode="HTML",
            reply_markup=back_kb("back_to_payment")
        )
    except Exception as e:
        logger.error(f"Error in xmr_payment: {e}")

@dp.callback_query(F.data == "why_deposit")
async def why_deposit(callback: types.CallbackQuery):
    try:
        await callback.answer()
        await callback.message.edit_text(
            "❕ Залог нужен для: ❕\n\n• Подтверждения серьезности намерений\n• Доступа к закрытым материалам и ресурсам команды\n•Фильтрации случайных людей и недобросовестных участников\n\nЗалог возвращается при выходе из тимы.",
            reply_markup=back_kb("back_to_payment")
        )
    except Exception as e:
        logger.error(f"Error in why_deposit: {e}")

@dp.callback_query(F.data.startswith("back_"))
async def back_handler(callback: types.CallbackQuery):
    try:
        await callback.answer()
        if callback.data == 'back_to_main':
            await callback.message.delete()
            await send_welcome(callback.message)
        elif callback.data == 'back_to_payment':
            await callback.message.edit_text(
                f"💰 Вступление в тиму Money Montana 💰\n\nДля прохода в тиму необходимо внести залог в размере {DEPOSIT_AMOUNT}\n\nВыберите способ оплаты:",
                reply_markup=payment_methods_kb()
            )
    except Exception as e:
        logger.error(f"Error in back_handler: {e}")
# ===================== WEBHOOK НАСТРОЙКА =====================
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Bot started at {WEBHOOK_URL}")

app = web.Application()
app.on_startup.append(on_startup)
app.router.add_post(WEBHOOK_PATH, lambda r: web.Response())

async def start_webhook():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(start_webhook())
