from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from .Context import CustomContext
from General.DataBase import *
from .States import MainStates
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .Keyboards import *
from datetime import time
from General import get_report_df
from sqlalchemy import and_
import re
import calendar
import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import json
import asyncio

def get_dates_with_no_data(dates: list[date]) -> list[date]:
    dates_no_data = []
    earliest_date = min(dates)
    number_of_days_from_earliest = (datetime.now().date() - earliest_date).days
    for i in range(number_of_days_from_earliest):
        if (earliest_date + timedelta(days=i)) not in dates:
            dates_no_data.append(min(dates) + timedelta(days=i))
    return dates_no_data

async def notification(context: CustomContext):
    session = context.bot_data.session_maker()
    data = session.query(DataSource).all()
    dates = [d.date for d in data]
    dates_no_data = get_dates_with_no_data(dates)
    with open("settings.json", "r") as f:
        s = json.load(f)
        user_id = s["user_id"]
        if len(dates_no_data) > 0:
            await context.bot.send_message(chat_id=user_id, text="Пожалуйста, не забудьте заполнить отчет (/enter_data)\n"\
                + "Незаполнены отчеты за следующие даты:" + "\n".join([d.strftime("%d.%m.%Y") for d in dates_no_data]))
        else:
            print("All reports are filled")
            await asyncio.sleep(1)
    session.close()


async def start(update: Update, context: CustomContext):
    user_id, admin_id = None, None
    with open("settings.json", "r") as f:
        s = json.load(f)
        user_id = s["user_id"]
        admin_id = s["admin_id"]
    if update.effective_message.from_user.id == admin_id:
        await update.effective_message.reply_text("Вы идентифицированы как администратор")
    elif update.effective_message.from_user.id == user_id:
        await update.effective_message.reply_text("Вы идентифицированы как пользователь")
        has_job = len(context.job_queue.get_jobs_by_name(f"notification")) > 0
        if not has_job:
            context.job_queue.run_repeating(callback=notification, interval=timedelta(minutes=60), first=0, name="notification")
    else:
        update.effective_message.reply_text("Вы не идентифицированы")

