from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from General.DataBase import ReportInterval
from datetime import date
from MainModule.Context import UserData

class UserEnterDataMenuKeyboard(InlineKeyboardMarkup):
    B_DATE = "Дата"
    B_COLLECTOR_SALARY = "Сборщик"
    B_DRIVERS_SALARY = "Водители"
    B_ADDITIONAL_COSTS = "Доп. расходы"
    B_DELIVERIES_NUMBER = "Количество доставок"
    B_DELIVERIES_INTERNAL = "Внутренние услуги"
    B_DELIVERIES_DISTANCE = "Дистанция"
    B_DRIVER_HOURS = "Часов работы водителей"
    B_SAVE = "✅ Сохранить"
    CB_DATE = "date"
    CB_COLLECTOR_SALARY = "cs"
    CB_DRIVERS_SALARY = "ds"
    CB_ADDITIONAL_COSTS = "ac"
    CB_DELIVERIES_NUMBER = "dn"
    CB_DELIVERIES_INTERNAL = "di"
    CB_DELIVERIES_DISTANCE = "dd"
    CB_DRIVER_HOURS = "dh"
    CB_SAVE = "save"
    def __init__(self, user_data: UserData):
        keyboard = []
        date_text = self.B_DATE + ":" + str(user_data.date) or "Не указано"
        cs_text = self.B_COLLECTOR_SALARY + ":" + str(user_data.collector_salary) or "Не указано"
        ds_text = self.B_DRIVERS_SALARY + ":" + str(user_data.drivers_salary) or "Не указано"
        ac_text = self.B_ADDITIONAL_COSTS + ":" + str(user_data.additional_costs) or "Не указано"
        dn_text = self.B_DELIVERIES_NUMBER + ":" + str(user_data.deliveries_number) or "Не указано"
        di_text = self.B_DELIVERIES_INTERNAL + ":" + str(user_data.deliveries_internal) or "Не указано"
        dd_text = self.B_DELIVERIES_DISTANCE + ":" + str(user_data.deliveries_distance) or "Не указано"
        dh_text = self.B_DRIVER_HOURS + ":" + str(user_data.driver_hours) or "Не указано"
        keyboard.append([InlineKeyboardButton(date_text, callback_data=self.CB_DATE)])
        keyboard.append([InlineKeyboardButton(cs_text, callback_data=self.CB_COLLECTOR_SALARY)])
        keyboard.append([InlineKeyboardButton(ds_text, callback_data=self.CB_DRIVERS_SALARY)])
        keyboard.append([InlineKeyboardButton(ac_text, callback_data=self.CB_ADDITIONAL_COSTS)])
        keyboard.append([InlineKeyboardButton(dn_text, callback_data=self.CB_DELIVERIES_NUMBER)])
        keyboard.append([InlineKeyboardButton(di_text, callback_data=self.CB_DELIVERIES_INTERNAL)])
        keyboard.append([InlineKeyboardButton(dd_text, callback_data=self.CB_DELIVERIES_DISTANCE)])
        keyboard.append([InlineKeyboardButton(dh_text, callback_data=self.CB_DRIVER_HOURS)])
        if all([user_data.collector_salary, 
                user_data.drivers_salary, 
                user_data.additional_costs, 
                user_data.deliveries_number, 
                user_data.deliveries_internal, 
                user_data.deliveries_distance, 
                user_data.driver_hours]):
            keyboard.append([InlineKeyboardButton(self.B_SAVE, callback_data=self.CB_SAVE)])
        super().__init__(keyboard)


class BackInlineKeyboard(InlineKeyboardMarkup):
    CB_BACK = "back"
    def __init__(self):
        super().__init__([
            [InlineKeyboardButton("Назад", callback_data=self.CB_BACK)]
        ])
