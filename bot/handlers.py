import os
import random
import dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, MessageEntity, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    BaseHandler,
)

from vector_search import VectorSearch
from ratelimit import RateLimiter
from middleware import admin_only


class Handlers:
    def __init__(self):
        dotenv.load_dotenv()

        self.toggle_on = True
        self.min_words = int(os.getenv("MIN_WORDS", 5))
        self.random_treshold = int(os.getenv("RANDOM_TRESHOLD", 5))
        self.ratelimit = True
        self.ratelimit_sec = int(os.getenv("RATELIMIT_SEC", 30))

        self.admin_ids = set(map(int, os.getenv("TELEGRAM_ADMIN_IDS", "").split()))
        self.message_ratelimit = RateLimiter(self.ratelimit_sec)
        self.vector_search = VectorSearch()

    async def start_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        await update.message.reply_text("Салют всем моим братьям")

    async def id(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            update.effective_user.id,
            entities=[
                MessageEntity(
                    offset=0,
                    length=len(str(update.effective_user.id)),
                    type=MessageEntity.CODE,
                )
            ],
        )

    @admin_only
    async def set_random_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        try:
            num = int(update.message.text.split()[1])
        except Exception:
            await update.message.reply_text(
                "Использование: `/setrandom 6` значения (1-10). 0, чтобы выключть"
            )
            return

        self.random_treshold = num

        await update.message.reply_text(f"Рандом теперь {self.random_treshold} в пределах 1-10")

    @admin_only
    async def toggle_ratelimit_callback(
        self, update: Update, _: ContextTypes.DEFAULT_TYPE
    ) -> None:
        query = update.callback_query

        self.ratelimit = not self.ratelimit

        await query.answer()
        await query.edit_message_reply_markup(self.settings_keyboard())

    @admin_only
    async def set_ratelimit(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            num = int(update.message.text.split()[1])
        except Exception:
            await update.message.reply_text(
                "Использование: `/setratelimit 30` - сколько секунд рейтлимитить сообщения"
            )
            return

        self.ratelimit_sec = num
        self.message_ratelimit = RateLimiter(self.ratelimit_sec)

        await update.message.reply_text(
            f"Рейтлимит обновлен до {self.ratelimit_sec} секунд"
        )

    def settings_keyboard(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Рубильник ✅", callback_data="settings_bot_off"
                    )
                    if self.toggle_on
                    else InlineKeyboardButton(
                        "Рубильник ❌", callback_data="settings_bot_on"
                    ),
                    InlineKeyboardButton(
                        "Ratelimit ✅", callback_data="settings_ratelimit_off"
                    )
                    if self.ratelimit
                    else InlineKeyboardButton(
                        "Ratelimit ❌", callback_data="settings_ratelimit_on"
                    ),
                    InlineKeyboardButton(
                        f"🎲 Рандом: {self.random_treshold} / 10",
                        callback_data="increment_random",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        f"⬆️ Порог символов: {self.min_words}",
                        callback_data="increment_min_words",
                    ),
                    InlineKeyboardButton(
                        "Понизить ⬇️", callback_data="decrement_min_words"
                    ),
                ],
                [
                    InlineKeyboardButton("🏃‍♂️‍➡️ Закрыть", callback_data="delete"),
                ],
            ]
        )

    @admin_only
    async def settings(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "🔧 Настройки",
            reply_markup=self.settings_keyboard(),
            reply_to_message_id=update.message.id,
        )

    @admin_only
    async def toggle_on_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        query = update.callback_query

        self.toggle_on = query.data.endswith("on")

        await query.answer()
        await query.edit_message_reply_markup(self.settings_keyboard())

    @admin_only
    async def increment_random(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        query = update.callback_query

        self.random_treshold += 1
        if self.random_treshold > 10:
            self.random_treshold = 0
            await query.answer()
            return

        await query.answer()
        await query.edit_message_reply_markup(self.settings_keyboard())

    @admin_only
    async def decrement_min_words(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        query = update.callback_query

        if self.min_words > 0:
            self.min_words -= 5
            await query.answer()
            return

        await query.answer()
        await query.edit_message_reply_markup(self.settings_keyboard())

    @admin_only
    async def increment_min_words(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        query = update.callback_query

        self.min_words += 5
        if self.min_words > 50:
            self.random_treshold = 0
            await query.answer()
            return

        await query.answer()
        await query.edit_message_reply_markup(self.settings_keyboard())

    @admin_only
    async def delete_msg(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        query = update.callback_query

        await query.answer()
        await query.delete_message()

    async def message_handler(
        self, update: Update, _: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if not self.toggle_on:
            return

        text = update.message.text

        if (
            len(text) < self.min_words
            or random.randint(1, 10) < self.random_treshold
            or (
                self.ratelimit
                and not self.message_ratelimit.is_allowed(update.effective_chat.id)
            )
        ):
            return

        try:
            result = self.vector_search.search(update.message.text)
        except Exception as e:
            await update.message.reply_text(f"Упс, белый: {e}")
            return

        await update.message.reply_text(result)

    def collect_handlers(self) -> list[BaseHandler]:
        return [
            CommandHandler("start", self.start_command),
            CommandHandler("id", self.id),
            CommandHandler("setrandom", self.set_random_command),
            CommandHandler("setratelimit", self.set_ratelimit),
            CommandHandler("settings", self.settings),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler),
            CallbackQueryHandler(self.toggle_on_callback, "^settings_bot_(on|off)$"),
            CallbackQueryHandler(
                self.toggle_ratelimit_callback, "^settings_ratelimit_(on|off)$"
            ),
            CallbackQueryHandler(self.increment_random, "^increment_random$"),
            CallbackQueryHandler(self.decrement_min_words, "^decrement_min_words$"),
            CallbackQueryHandler(self.increment_min_words, "^increment_min_words$"),
            CallbackQueryHandler(self.delete_msg, "^delete$"),
        ]

    def supported_commands(self) -> list[tuple[str, str]]:
        return [
            ("start", "start"),
            ("id", "get my id"),
            ("settings", "settings menu"),
            ("setrandom", "/setrandom 5 (from 1 to 10)"),
            ("setratelimit", "/setratelimit 5 (sec timeout)"),
        ]
