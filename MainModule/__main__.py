from telegram.constants import ParseMode
from telegram.ext import (
    ConversationHandler,
    Application,
    ContextTypes,
    MessageHandler,
    TypeHandler,
    Defaults,
    filters,
    CommandHandler,
    CallbackQueryHandler
)
import traceback
import json
from .States import MainStates
from .Views import *
from .Context import *
from datetime import timezone
from General import re_prefix
from UserModule import user_conv_handler
#from AdminModule import admin_conv_handler

general_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states = {
    },
    fallbacks=[],
    name="main_conv",
    per_chat=False,
    allow_reentry=True
)


context_types = ContextTypes(context=CustomContext, bot_data=BotData, user_data=UserData)

application = Application.builder().token("6499782978:AAEHEI87xWwOW1uHux8pYJTZUaZY3zjpCTY").context_types(context_types).defaults(Defaults(parse_mode=ParseMode.HTML, protect_content=False, tzinfo=timezone(timedelta(hours=3)))).build()

application.add_handler(general_conv_handler)
application.add_handler(user_conv_handler)


if __name__ == "__main__":
    print("Starting polling!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)