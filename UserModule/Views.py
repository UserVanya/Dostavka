from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
#import ConversationHandler
from telegram.ext import ConversationHandler
from MainModule.Context import CustomContext
from General.DataBase import *
from .States import MainStates
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .Keyboards import *
from datetime import time
from General import get_report_df, save_delivery_excel
from sqlalchemy import and_
import re
import calendar
import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import json
from telegram import Message
#import sleep
from time import sleep
async def delete_msg(update: Update, context: CustomContext, msg: Message):
    try:
        await context.bot.delete_message(context.user_data.msg.chat_id, msg.message_id)
    except:
        pass

async def enter_data_show_main(update: Update, context: CustomContext):
    msg = await update.effective_message.reply_text("Выберите поле для заполнения", reply_markup=UserEnterDataMenuKeyboard(context.user_data))
    context.user_data.msg = msg
    return MainStates.MAIN_MENU

async def back_from_enter_data(update: Update, context: CustomContext):
    context.user_data.msg = await update.effective_message.edit_text("Выберите поле для заполнения", reply_markup=UserEnterDataMenuKeyboard(context.user_data))
    return MainStates.MAIN_MENU

async def enter_particular_data(update: Update, context: CustomContext):
    cb_data = update.callback_query.data
    context.user_data.last_cb = cb_data
    text = "Введите значение"
    if cb_data == UserEnterDataMenuKeyboard.CB_DATE:
        text = "Введите дату в формате ДД.ММ.ГГГГ"
    elif cb_data == UserEnterDataMenuKeyboard.CB_COLLECTOR_SALARY:
        text = "Введите зарплату сборщика"
    elif cb_data == UserEnterDataMenuKeyboard.CB_DRIVERS_SALARY:
        text = "Введите зарплату водителей общую"
    elif cb_data == UserEnterDataMenuKeyboard.CB_ADDITIONAL_COSTS:
        text = "Введите дополнительные расходы"
    elif cb_data == UserEnterDataMenuKeyboard.CB_DELIVERIES_NUMBER:
        text = "Введите количество доставок"
    elif cb_data == UserEnterDataMenuKeyboard.CB_DELIVERIES_INTERNAL:
        text = "Введите количество внутренних доставок"
    elif cb_data == UserEnterDataMenuKeyboard.CB_DELIVERIES_DISTANCE:
        text = "Введите дистанцию"
    elif cb_data == UserEnterDataMenuKeyboard.CB_DRIVER_HOURS:
        text = "Введите количество часов работы водителей"
    msg = await update.effective_message.edit_text(text, reply_markup=BackInlineKeyboard())
    context.user_data.msg = msg
    return MainStates.ASKING_DATA

async def save_particular_data(update: Update, context: CustomContext):
    data = update.effective_message.text
    cb_data = context.user_data.last_cb
    if cb_data == UserEnterDataMenuKeyboard.CB_DATE:
        try:
            data = datetime.strptime(data, "%d.%m.%Y").date()
            if data >= datetime.now().date():
                raise IndexError 
        except ValueError:
            await update.effective_message.reply_text("Неверный формат даты")
            return MainStates.ASKING_DATA
        except IndexError:
            await update.effective_message.reply_text("Дата не может быть больше текущей")
            return MainStates.ASKING_DATA
    elif cb_data in [UserEnterDataMenuKeyboard.CB_COLLECTOR_SALARY, 
                     UserEnterDataMenuKeyboard.CB_DRIVERS_SALARY, 
                     UserEnterDataMenuKeyboard.CB_ADDITIONAL_COSTS, 
                     UserEnterDataMenuKeyboard.CB_DELIVERIES_NUMBER, 
                     UserEnterDataMenuKeyboard.CB_DELIVERIES_INTERNAL, 
                     UserEnterDataMenuKeyboard.CB_DELIVERIES_DISTANCE, 
                     UserEnterDataMenuKeyboard.CB_DRIVER_HOURS]:
        try:
            data = float(data)
            if data < 0:
                raise IndexError
        except ValueError:
            await update.effective_message.reply_text("Неверный формат числа")
            return MainStates.ASKING_DATA
        except IndexError:
            await update.effective_message.reply_text("Число не может быть отрицательным")
            return MainStates.ASKING_DATA
    if cb_data == UserEnterDataMenuKeyboard.CB_DATE:
        context.user_data.date = data
    elif cb_data == UserEnterDataMenuKeyboard.CB_COLLECTOR_SALARY:
        context.user_data.collector_salary = data
    elif cb_data == UserEnterDataMenuKeyboard.CB_DRIVERS_SALARY:
        context.user_data.drivers_salary = data
    elif cb_data == UserEnterDataMenuKeyboard.CB_ADDITIONAL_COSTS:
        context.user_data.additional_costs = data
    elif cb_data == UserEnterDataMenuKeyboard.CB_DELIVERIES_NUMBER:
        context.user_data.deliveries_number = data
    elif cb_data == UserEnterDataMenuKeyboard.CB_DELIVERIES_INTERNAL:
        context.user_data.deliveries_internal = data
    elif cb_data == UserEnterDataMenuKeyboard.CB_DELIVERIES_DISTANCE:
        context.user_data.deliveries_distance = data
    elif cb_data == UserEnterDataMenuKeyboard.CB_DRIVER_HOURS:
        context.user_data.driver_hours = data
    
    print(context.user_data.__dict__)
    await update.effective_message.reply_text("Данные сохранены")
    await delete_msg(update, context, context.user_data.msg)
    return await enter_data_show_main(update, context)

async def save(update: Update, context: CustomContext):
    session = context.bot_data.session_maker()
    
    date_data = session.query(DataSource).filter(DataSource.date == context.user_data.date).one_or_none()
    if date_data:
        date_data.collector_salary = context.user_data.collector_salary
        date_data.drivers_salary = context.user_data.drivers_salary
        date_data.additional_costs = context.user_data.additional_costs
        date_data.deliveries_total = context.user_data.deliveries_number
        date_data.deliveries_internal = context.user_data.deliveries_internal
        date_data.deliveries_distance = context.user_data.deliveries_distance
        date_data.driver_hours = context.user_data.driver_hours
    else:
        data = DataSource(
            date=context.user_data.date,
            collector_salary=context.user_data.collector_salary,
            drivers_salary=context.user_data.drivers_salary,
            additional_costs=context.user_data.additional_costs,
            deliveries_total=context.user_data.deliveries_number,
            deliveries_internal=context.user_data.deliveries_internal,
            deliveries_distance=context.user_data.deliveries_distance,
            driver_hours=context.user_data.driver_hours
        )
        session.add(data)
    session.commit()
    session.close()
    await update.effective_message.reply_text("Данные сохранены")
    await delete_msg(update, context, context.user_data.msg)
    file_path = save_delivery_excel(
        date=context.user_data.date,
        collector_salary=context.user_data.collector_salary,
        drivers_salary=context.user_data.drivers_salary,
        additional_costs=context.user_data.additional_costs,
        deliveries_total=context.user_data.deliveries_number,
        deliveries_internal=context.user_data.deliveries_internal,
        deliveries_distance=context.user_data.deliveries_distance,
        driver_hours=context.user_data.driver_hours
    )
    sleep(1)
    #send_report
    document_file_input = open(file_path, "rb")
    await context.bot.send_document(chat_id=update.effective_user.id, document=document_file_input, filename=f"Отчет_{context.user_data.date.strftime('%d.%m.%Y')}.xlsx")
    with open("settings.json", "r") as f:
        s = json.load(f)
        admin_id = s["admin_id"]
        await context.bot.send_document(chat_id=admin_id, document=document_file_input, filename=f"Отчет_{context.user_data.date.strftime('%d.%m.%Y')}.xlsx")
    sleep(1)
    document_file_input.close()
    return ConversationHandler.END