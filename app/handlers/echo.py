# Handles ONLY the /echo command
async def echo_command(update, context):
    """Handler for /echo command"""
    if context.args:
        text = ' '.join(context.args)
        await update.message.reply_text(f"You said: {text}")
    else:
        await update.message.reply_text("Please provide some text after /echo")