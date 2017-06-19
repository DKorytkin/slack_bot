#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Denis'

import json

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    create_engine,
    DateTime,
    Date,
    Enum,
    TypeDecorator
)

Base = declarative_base()


class ArrayType(TypeDecorator):
    """ Sqlite-like does not support arrays.
        Let's use a custom type decorator.

        See http://docs.sqlalchemy.org/en/latest/core/types.html#sqlalchemy.types.TypeDecorator
    """
    impl = String

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)

    def copy(self):
        return ArrayType(self.impl.length)


class EnumStatus(Enum):
    orderly = 1
    vacation = 2
    teaching = 3
    passing = 4


class EnumSentry(Enum):
    duty = 1


class AllBugs(Base):
    __tablename__ = 'all_bugs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_name = Column(String(20))
    priority = Column(String(10))
    description = Column(String(500))
    developer_name = Column(String(100))
    date_created = Column(DateTime)
    date_resolution = Column(DateTime)
    ready_for_dev = Column(DateTime)
    in_dev = Column(DateTime)
    ready_for_test = Column(DateTime)
    elapsed_time_for_task_in_seconds = Column(Integer)
    created = Column(Date)
    developer_id = Column(Integer, ForeignKey('team.id'))

    def __init__(self, task_name, priority, description, developer_name,
                 date_created, date_resolution, ready_for_dev, in_dev,
                 ready_for_test, elapsed_time_for_task_in_seconds,
                 created, developer_id):
        self.task_name = task_name
        self.priority = priority
        self.description = description
        self.developer_name = developer_name
        self.date_created = date_created
        self.date_resolution = date_resolution
        self.ready_for_dev = ready_for_dev
        self.in_dev = in_dev
        self.ready_for_test = ready_for_test
        self.elapsed_time_for_task_in_seconds = (
            elapsed_time_for_task_in_seconds)
        self.created = created
        self.developer_id = developer_id

    def __repr__(self):
        return "AllBugs(%r, %r, %r, %r, %r, %r, %r, %r, %r, %r, %r, %r)" % (
            self.task_name,
            self.priority,
            self.description,
            self.developer_name,
            self.date_created,
            self.date_resolution,
            self.ready_for_dev,
            self.in_dev,
            self.ready_for_test,
            self.elapsed_time_for_task_in_seconds,
            self.created,
            self.developer_id,
        )


class Team(Base):
    __tablename__ = 'team'

    id = Column(Integer, primary_key=True, autoincrement=True)
    blocker = Column(Integer)
    critical = Column(Integer)
    major = Column(Integer)
    minor = Column(Integer)
    trivial = Column(Integer)
    total = Column(Integer)
    vacation_boost = Column(Integer, default=0)
    name = Column(String(100))
    date_start = Column(Date)
    date_over = Column(Date)
    status = Column(Integer)
    sentry = Column(Integer)
    jira_url = Column(String(1000))

    def __init__(self, id, blocker, critical, major, minor, trivial, total,
                 vacation_boost, name, date_start, date_over,
                 status, sentry, jira_url):
        self.id = id
        self.blocker = blocker
        self.critical = critical
        self.major = major
        self.minor = minor
        self.trivial = trivial
        self.total = total
        self.vacation_boost = vacation_boost
        self.name = name
        self.date_start = date_start
        self.date_over = date_over
        self.status = status
        self.sentry = sentry
        self.jira_url = jira_url

    def __repr__(self):
        return "Team(%r, %r, %r, %r, %r, %r, %r, %r, %r, %r, %r, %r, %r, %r)"\
               % (
                    self.id,
                    self.blocker,
                    self.critical,
                    self.major,
                    self.minor,
                    self.trivial,
                    self.total,
                    self.vacation_boost,
                    self.name,
                    self.date_start,
                    self.date_over,
                    self.status,
                    self.sentry,
                    self.jira_url
                )


class BoostVacation(Base):
    __tablename__ = 'boost_vacations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    developer_id = Column(Integer, ForeignKey('team.id'))
    vacation_start = Column(Date)
    vacation_over = Column(Date)
    list_issues = Column(ArrayType)

    def __init__(self, developer_id, vacation_start, vacation_over, list_issues):
        self.developer_id = developer_id
        self.vacation_start = vacation_start
        self.vacation_over = vacation_over
        self.list_issues = list_issues

    def __repr__(self):
        return "Team(%r, %r, %r, %r)" % (
            self.developer_id,
            self.vacation_start,
            self.vacation_over,
            self.list_issues,
        )

engine = create_engine('sqlite:///team.db', echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
