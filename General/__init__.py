from telegram.ext import filters
from datetime import datetime, date
#from MainModule.Context import CustomContext
import hashlib
import pandas as pd
import json
import requests
import numpy as np
import xml.etree.ElementTree as ET
from enum import StrEnum
import math
from datetime import timedelta
from telegram import Update
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, date, time
import io
from Calculator import DeliveryFinancialTable

def count_week_days(date_from: date, date_to: date, week_day: int) -> int:
    count = 0
    first_date = [date_from + timedelta(days=i) for i in range(7) if (date_from + timedelta(days=i)).weekday() == week_day][0]

    weeks = (date_to - first_date).days // 7 + 1
    return weeks

class Param:
    def __init__(self, 
                 name: str,
                 uf_name: str, 
                 type_: str, 
                 aggregation_allowed: bool,
                 grouping_allowed:bool,
                 filtering_allowed:bool,
                 tags: list[str]) -> None:
        self.__name = name
        self.__uf_name = uf_name
        self.__type = type_
        self.__aggregation_allowed = aggregation_allowed
        self.__grouping_allowed = grouping_allowed
        self.__filtering_allowed = filtering_allowed
        self.__tags = tags
    
    @property
    def name(self):
        return self.__name
    @property
    def uf_name(self):
        return self.__uf_name
    @property
    def type_(self):
        return self.__type
    @property
    def aggregation_allowed(self):
        return self.__aggregation_allowed
    @property
    def grouping_allowed(self):
        return self.__grouping_allowed
    @property
    def filtering_allowed(self):
        return self.__filtering_allowed
    @property
    def tags(self):
        return self.__tags.copy()

    def __str__(self) -> str:
        return {
            self.name: {
                "name": self.uf_name,
                "type": self.type_,
                "aggregationAllowed": self.aggregation_allowed,
                "groupingAllowed": self.grouping_allowed,
                "filteringAllowed": self.filtering_allowed,
                "tags": self.tags
            }
        }.__str__()

def edit_df(df: pd.DataFrame, params: list[Param]) -> pd.DataFrame:
    def param_by_name(name: str):
        for param in params:
            if param.name == name:
                return param
        return None
    for column in df.columns:
        param = param_by_name(column)
        if param.type_ == "MONEY" or param.type_ == "AMOUNT":
            #such columns should be of type float, not str
            df[column] = df[column].apply(lambda x: float(x))
        if param.type_ == "DATE":
            #Fri Jun 14 00:00:00 MSK 2024 (str) to 14.06.2024 (date)
            df[column] = df[column].apply(lambda x: datetime.strptime(x, "%a %b %d %H:%M:%S MSK %Y").date() if x else None)
        if param.type_ == "DATETIME":
            #Fri Jun 14 00:00:00 MSK 2024 (str) to 14.06.2024 00:00:00 (datetime)
            df[column] = df[column].apply(lambda x: datetime.strptime(x, "%a %b %d %H:%M:%S MSK %Y") if x else None)
        if param.type_ == "ENUM":
            #if param.name is Delivery.IsDelivery, then DELIVERY_ORDER to Доставка, ORDER_WITHOUT_DELIVERY to Без доставки
            if param.name == "Delivery.IsDelivery":
                df[column] = df[column].apply(lambda x: "Доставка" if x == "DELIVERY_ORDER" else "Без доставки")
        df.fillna("", inplace=True)
    return df

class RevenueStandardInterval(StrEnum):
    TODAY = "Сегодня"
    YESTERDAY = "Вчера"
    CURRENT_WEEK = "Текущая неделя"
    LAST_WEEK = "Прошлая неделя"
    CURRENT_MONTH = "Текущий месяц"
    LAST_MONTH = "Прошлый месяц"
    CURRENT_YEAR = "Текущий год"
    def get_interval(self):
        now = datetime.now()
        if self == RevenueStandardInterval.TODAY:
            return now.date(), now.date()
        elif self == RevenueStandardInterval.YESTERDAY:
            return now.date() - timedelta(days=1), now.date() - timedelta(days=1)
        elif self == RevenueStandardInterval.CURRENT_WEEK:
            return now.date() - timedelta(days=now.weekday()), now.date()
        elif self == RevenueStandardInterval.LAST_WEEK:
            return now.date() - timedelta(days=now.weekday() + 7), now.date() - timedelta(days=now.weekday() + 1)
        elif self == RevenueStandardInterval.CURRENT_MONTH:
            return now.replace(day=1).date(), now.date()
        elif self == RevenueStandardInterval.LAST_MONTH:
            return (now.replace(day=1) - timedelta(days=1)).replace(day=1).date(), (now.replace(day=1) - timedelta(days=1)).date()
        elif self == RevenueStandardInterval.CURRENT_YEAR:
            return now.replace(month=1, day=1).date(), now.date()
        else:
            return None

def re_prefix(prefix: str):
    return f"^{prefix.strip()}.+$"

def re_prefix_filter(prefix: str):
    return filters.Regex(f"^{prefix.strip()}.+$")

def sha1_hash(password):
    sha1 = hashlib.sha1()
    sha1.update(password.encode('utf-8'))
    return sha1.hexdigest()

def read_xml(xml: str):
    # Parse the XML data
    root = ET.fromstring(xml)

    # Create a list to store data
    data = []

    # Iterate through each 'r' element and extract data
    for elem in root.findall('r'):
        row_data = {}
        for subelem in elem:
            row_data[subelem.tag] = subelem.text
        data.append(row_data)

    # Create DataFrame
    df = pd.DataFrame(data)
    return df

def get_report_df(feature_columns: list[str], 
                  result_columns: list[str], 
                  date_from: date, 
                  date_to: date) -> pd.DataFrame:
    s = None
    feature_columns += ["DeletedWithWriteoff", "OrderDeleted"]
    with open("settings.json", "r") as f:
        s = json.load(f)
    url = s["url"]
    port = s["port"]
    login = s["login"]
    pw = sha1_hash(s["password"])
    token_request = f'https://{url}:{port}/resto/api/auth?login={login}&pass={pw}'
    token = requests.get(token_request).text
    date_from_str = date_from.strftime("%d.%m.%Y")
    date_to_str = date_to.strftime("%d.%m.%Y")
    feature_str = "&".join([f"groupRow={col}" for col in feature_columns])
    result_str = "&".join([f"agr={col}" for col in result_columns])
    olap = f'https://{url}:{port}/resto/api/reports/olap?key={token}&report=SALES&from={date_from_str}&to={date_to_str}&{feature_str}&{result_str}'
    #print(olap)
    xml_olap = requests.get(olap).text
    #print(xml_olap)
    df = read_xml(xml_olap)
    #print(df)
    if not df.empty:
        df = df[df["DeletedWithWriteoff"] == "NOT_DELETED"]
        df = df[df["OrderDeleted"] == "NOT_DELETED"]
        df.drop(columns=["DeletedWithWriteoff", "OrderDeleted"], inplace=True)
        df = df.astype({col: "float" for col in result_columns})
    return df

def get_delivery_df(date_from: date, date_to: date) -> pd.DataFrame:
    df = get_report_df(
        [
            "Delivery.IsDelivery", 
            "RestorauntGroup", 
            "PayTypes",
            "DishCategory",
            "OriginName",
            "OrderType",
            "ItemSaleEventDiscountType"
        ], 
        [
            "DishDiscountSumInt",
            "DishSumInt",
            "ProductCostBase.ProductCost",
            "UniqOrderId.OrdersCount",
            "DiscountSum"
        ], 
        date_from,
        date_to
    )
    return df

def save_delivery_excel(date: date, collector_salary: int, drivers_salary: int, additional_costs: dict,
                 deliveries_total: int, deliveries_internal: int,  deliveries_distance: int, driver_hours: float):
    df = get_delivery_df(date, date)
    table = DeliveryFinancialTable(df,
                                   date,
                                   collector_salary,
                                   drivers_salary,
                                   additional_costs,
                                   deliveries_total,
                                   deliveries_internal,
                                   deliveries_distance,
                                   driver_hours)
    return table.save_to_excel(f"DeliveryFinancialTable_{date.strftime('%d.%m.%Y')}.xlsx")