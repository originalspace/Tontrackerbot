import logging
import typing
import tonsdk.utils

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    PicklePersistence,
    filters,
)
from uuid import uuid4
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

TOKEN: typing.Final = ''
BOT_USERNAME: typing.Final = ''
BOT_ID: typing.Final = ''

wallet = []


max = 3

async def get(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usage: /get uuid"""

    # Separate ID from command
    try:
        key = context.args[1]

    # Load value and send it to the user
        value = context.args[0]
        tonsdk.utils.Address(value)
        wallet.append(str(value) + f"({key})" )
        await update.message.reply_text("this is your list:\n\n" + '\n\n'.join([str(wallets) for wallets in wallet]))
    except ValueError: 
        await update.message.reply_text("write something valid")

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = context.args[0]
    tonsdk.utils.Address(value)
    for value in wallet:
        if value == wallet[0]:
            wallet.remove(value)
            await update.message.reply_text("deleted")

async def list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(', '.join([str(wallets) for wallets in wallet]))


if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('get', get))
    application.add_handler(CommandHandler("rem", delete))
    application.add_handler(CommandHandler("list", list))
    application.run_polling()