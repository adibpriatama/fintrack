# Handles ONLY the /start command
async def start_command(update, context):
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}! 👋\nI'm an example bot. Use /help to see what I can do."
    )