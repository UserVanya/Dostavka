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
user_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("enter_data", enter_data_show_main)],
    states = {
        MainStates.MAIN_MENU: [
            CallbackQueryHandler(enter_particular_data, pattern=UserEnterDataMenuKeyboard.CB_DATE),
            CallbackQueryHandler(enter_particular_data, pattern=UserEnterDataMenuKeyboard.CB_COLLECTOR_SALARY),
            CallbackQueryHandler(enter_particular_data, pattern=UserEnterDataMenuKeyboard.CB_DRIVERS_SALARY),
            CallbackQueryHandler(enter_particular_data, pattern=UserEnterDataMenuKeyboard.CB_ADDITIONAL_COSTS),
            CallbackQueryHandler(enter_particular_data, pattern=UserEnterDataMenuKeyboard.CB_DELIVERIES_NUMBER),
            CallbackQueryHandler(enter_particular_data, pattern=UserEnterDataMenuKeyboard.CB_DELIVERIES_INTERNAL),
            CallbackQueryHandler(enter_particular_data, pattern=UserEnterDataMenuKeyboard.CB_DELIVERIES_DISTANCE),
            CallbackQueryHandler(enter_particular_data, pattern=UserEnterDataMenuKeyboard.CB_DRIVER_HOURS),
            CallbackQueryHandler(save, pattern=UserEnterDataMenuKeyboard.CB_SAVE)
        ],
        MainStates.ASKING_DATA: [
            MessageHandler(filters.TEXT, save_particular_data),
            CallbackQueryHandler(back_from_enter_data, pattern=BackInlineKeyboard.CB_BACK)
        ]
    },
    fallbacks=[CommandHandler("enter_data", enter_data_show_main)],
    name="user_conv",
    per_chat=False,
    allow_reentry=True
)