import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder

from handlers import Handlers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)


def main():
    h = Handlers()

    async def post_init(application):
        await application.bot.set_my_commands(h.supported_commands())

    application = (
        ApplicationBuilder()
        .token(str(os.getenv("TELEGRAM_BOT_TOKEN")))
        .post_init(post_init)
        .build()
    )

    for handler in h.collect_handlers():
        application.add_handler(handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
