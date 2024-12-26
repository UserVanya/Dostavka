from telegram.ext import CallbackContext, ExtBot
from typing import Optional
from telegram.ext import Application
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telegram import Message
from sqlalchemy.orm.session import Session
from typing import DefaultDict
from General.DataBase import *
import os
from enum import Enum
from datetime import datetime, timedelta, time, date
from General import get_report_df
from General.DataBase import ReportInterval
import pandas as pd
import json
from collections import defaultdict

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


class UserData:
    def __init__(self) -> None:
        self.session: Session = None
        self.collector_salary: float = None
        self.drivers_salary: float = None
        self.additional_costs: float = None
        self.deliveries_number: int = None
        self.deliveries_internal: int = None
        self.deliveries_distance: int = None
        self.driver_hours: int = None
        self.date: date = None
        self.msg: Message = None
        self.last_cb = None
class BotData:
    def __init__(self) -> None:
        self.db_name: str = "bot_db.sqlite3"
        has_db = os.path.isfile(self.db_name)    
        self.engine = create_engine(f"sqlite:///{self.db_name}", pool_size=10, max_overflow=20)
        self.session_maker = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self.last_update = datetime.now()
        self.__params: list[Param] = []
        with open("rows.json", encoding='utf-8') as f:
            data = json.loads(f.read())
            unique_types = []
            for name, item in data.items():
                item: Param = item
                unique_types.append(item["type"])
                self.__params.append(Param(name, item["name"],
                                                 item["type"],
                                                 item["aggregationAllowed"],
                                                 item["groupingAllowed"],
                                                 item["filteringAllowed"],
                                                 item["tags"]))
    
    def param_by_name(self, name: str):
        for param in self.__params:
            if param.name == name:
                return param
        return None
    
    def param_by_uf_name(self, uf_name: str):
        for param in self.__params:
            if param.uf_name == uf_name:
                return param
        return None

    def name_by_uf_name(self, uf_name: str):
        for param in self.__params:
            if param.uf_name == uf_name:
                return param.name
        return None
    
    def uf_name_by_name(self, name: str):
        for param in self.__params:
            if param.name == name:
                return param.uf_name
        return None
    
    def feature_columns_by_tag(self, tag: str):
        columns = []
        for param in self.__params:
            if tag in param.tags and param.grouping_allowed:
                columns.append(param.uf_name)
        return columns

    def aggregation_columns_by_tag(self, tag: str):
        columns = []
        for param in self.__params:
            if tag in param.tags and param.aggregation_allowed:
                columns.append(param.uf_name)
        return columns

    @property
    def params(self):
        return self.__params.copy()
    
    @property
    def param_feature_tags(self):
        tags = []
        for param in self.__params:
            if param.grouping_allowed:
                tags.extend(param.tags)
        return list(set(tags))
    
    @property
    def param_aggregation_tags(self):
        tags = []
        for param in self.__params:
            if param.aggregation_allowed:
                tags.extend(param.tags)
        return list(set(tags))

    @property
    def can_obtain_gains(self):
        update_period = None
        with open("settings.json", "r") as f:
            s = json.load(f)
            update_period = s["update_period_seconds"]
        return (datetime.now() - self.last_update).seconds > update_period
    @property
    def time_left_seconds(self):
        update_period = None
        with open("settings.json", "r") as f:
            s = json.load(f)
            update_period = s["update_period_seconds"]
        return update_period - (datetime.now() - self.last_update).seconds
class CustomContext(CallbackContext[ExtBot, UserData, dict, BotData]):
    """Custom class for context."""

    def __init__(
        self,
        application: Application,
        chat_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ):
        super().__init__(application=application, chat_id=chat_id, user_id=user_id)
        self._message_id: Optional[int] = None
        