from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey, Table, Date, Boolean, Time
from sqlalchemy.orm import relationship
from enum import StrEnum
from datetime import datetime, timedelta

class ReportInterval(StrEnum):
    TODAY = "Сегодня"
    YESTERDAY = "Вчера"
    CURRENT_WEEK = "Текущая неделя"
    LAST_WEEK = "Прошлая неделя"
    CURRENT_MONTH = "Текущий месяц"
    LAST_MONTH = "Прошлый месяц"
    CURRENT_YEAR = "Текущий год"
    LAST_YEAR = "Прошлый год"
    MANUAL = "Вручную"
    def get_interval(self):
        now = datetime.now()
        if self == ReportInterval.TODAY:
            return now.date(), now.date()
        elif self == ReportInterval.YESTERDAY:
            return now.date() - timedelta(days=1), now.date() - timedelta(days=1)
        elif self == ReportInterval.CURRENT_WEEK:
            return now.date() - timedelta(days=now.weekday()), now.date()
        elif self == ReportInterval.LAST_WEEK:
            return now.date() - timedelta(days=now.weekday() + 7), now.date() - timedelta(days=now.weekday() + 1)
        elif self == ReportInterval.CURRENT_MONTH:
            return now.replace(day=1).date(), now.date()
        elif self == ReportInterval.LAST_MONTH:
            return (now.replace(day=1) - timedelta(days=1)).replace(day=1).date(), (now.replace(day=1) - timedelta(days=1)).date()
        elif self == ReportInterval.CURRENT_YEAR:
            return now.replace(month=1, day=1).date(), now.date()
        elif self == ReportInterval.LAST_YEAR:
            return now.replace(year=now.year - 1, month=1, day=1).date(), now.replace(year=now.year - 1, month=12, day=31).date()
        else:
            return None

Base = declarative_base()



class DataSource(Base):
    __tablename__ = "data_sources"
    date = Column(Date, primary_key=True)
    collector_salary = Column(Float)
    drivers_salary = Column(Float)
    additional_costs = Column(Float)
    deliveries_total = Column(Integer)
    deliveries_internal = Column(Integer)
    deliveries_distance = Column(Integer)
    driver_hours = Column(Float)