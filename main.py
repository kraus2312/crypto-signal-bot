
from aiogram import Bot, Dispatcher, executor, types
from config import BOT_TOKEN
from handlers import user
from handlers.subscribe import register_subscribe_handlers
from handlers.admin import register_admin_handlers, admin

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

user.register(dp)
admin.register(dp)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
