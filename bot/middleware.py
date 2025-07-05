from telegram import Update


def admin_only(func):
    async def wrapper(self, update: Update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in self.admin_ids:
            if update.callback_query is not None:
                await update.callback_query.answer("❌ вы не админ, а-та-та")

            return

        return await func(self, update, *args, **kwargs)

    return wrapper
