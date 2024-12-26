from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from General.DataBase import ReportInterval
from datetime import date

class UserMainMenuKeyboard(InlineKeyboardMarkup):
    B_DATE = "Дата"
    B_COLLECTOR_SALARY = "Сборщик"
    B_DRIVERS_SALARY = "Водители"
    B_ADDITIONAL_COSTS = "Доп. расходы"
    B_DELIVERIES_NUMBER = "Количество доставок"
    B_DELIVERIES_INTERNAL = "Внутренние услуги"
    B_DELIVERIES_DISTANCE = "Дистанция"
    B_SAVE = "✅ Сохранить"
    CB_DATE = "date"
    CB_COLLECTOR_SALARY = "cs"
    CB_DRIVERS_SALARY = "ds"
    CB_ADDITIONAL_COSTS = "ac"
    CB_DELIVERIES_NUMBER = "dn"
    CB_DELIVERIES_INTERNAL = "di"
    CB_DELIVERIES_DISTANCE = "dd"
    CB_SAVE = "save"
    def __init__(self):
        super().__init__([
            [InlineKeyboardButton(self.B_COLLECTOR_SALARY, callback_data=self.CB_COLLECTOR_SALARY)],
            [InlineKeyboardButton(self.B_DRIVERS_SALARY, callback_data=self.CB_DRIVERS_SALARY)],
            [InlineKeyboardButton(self.B_ADDITIONAL_COSTS, callback_data=self.CB_ADDITIONAL_COSTS)],
            [InlineKeyboardButton(self.B_DELIVERIES_NUMBER, callback_data=self.CB_DELIVERIES_NUMBER)],
            [InlineKeyboardButton(self.B_DELIVERIES_INTERNAL, callback_data=self.CB_DELIVERIES_INTERNAL)],
            [InlineKeyboardButton(self.B_DELIVERIES_DISTANCE, callback_data=self.CB_DELIVERIES_DISTANCE)],
            [InlineKeyboardButton(self.B_SAVE, callback_data=self.CB_SAVE)]
        ])