#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Denis'

from datetime import datetime
from math import ceil
from sqlalchemy import func

import requests
from models import session, Team, EnumEqualPoints, EnumSentry

from parse_data import update_all_issues

CAT_ENDPOINT = "http://random.cat/meow"
DEFAULT_CAT = "http://media.topito.com/wp-content/uploads/2013/01/code-12.gif"
equal_type = EnumEqualPoints
# Список праздников, не рабочих дней
holidays = [
    '01.01.16', '07.01.16',
    '08.03.16',
    '01.05.16', '03.05.16', '09.05.16',
    '20.06.16', '28.06.16',
    '24.08.16',
    '14.10.16'
]

# Список выходных Sunday
day_off = ['Saturday']


def get_random_cat():
    r = requests.get(CAT_ENDPOINT)
    try:
        url = r.json()['file']
    except:
        url = DEFAULT_CAT
    return url


def update_equal_points(query):
    """
    equal_points:
    1 = Одинаковое кол-во поинтов
    2 = Отпуск
    3 = Макс преподает
    """
    def exception_dev(developers):
        for developer in developers:
            # Проверка в четверг для Макса Thursday
            if datetime.now().strftime('%A') == 'Thursday' and developer.id == 3:
                session.query(Team).filter(Team.id == developer.id).update({'equal_points': equal_type.teaching}, False)
            elif developer.date_start is None:
                session.query(Team).filter(Team.id == developer.id).update({'equal_points': None}, False)
            elif developer.date_start <= datetime.now().date() <= developer.date_over:
                session.query(Team).filter(Team.id == developer.id).update({'equal_points': equal_type.vacation}, False)
            else:
                session.query(Team).filter(Team.id == developer.id).update({'equal_points': None}, False)
        session.commit()

    exception_dev(query)

    min_point = session.query((func.min(Team.total))).filter(Team.equal_points == None).scalar()
    developers = session.query(Team).order_by(Team.total.desc())
    for dev in developers:
        # Номинант на дежурство
        if dev.total == min_point and dev.date_start is None:
            session.query(Team).filter(Team.id == dev.id).update({'equal_points': equal_type.orderly}, False)

    session.commit()


def choose_developer(query, sum_equal_points, sum_sentrys):
    """
    if have some developers equal points
    """
    for dev in query:
        if sum_equal_points == sum_sentrys:
            session.query(Team).update({'sentry': None}, False)
            session.commit()
            # winner = dev.name
            # session.query(Team).filter(Team.id == dev.id).update({'sentry': 1}, False)
        if dev.equal_points == 1 and dev.sentry is None:
            winner = dev.name
            session.query(Team).filter(Team.id == dev.id).update({'sentry': EnumSentry.duty}, False)
            session.commit()
            return winner

        # TODO delete this code after test
        # if query.id == dev_id and query.equal_points == 1 and equal_points == sentrys:
        #     winner = dev_name
        #     session.query(Team).update({'sentry': None}, False)
        #     session.commit()
        #     session.query(Team).filter(Team.id == dev_id).update({'sentry': 1}, False)
        #     session.commit()
        #     flag = True
        #     break
        # elif query.id == dev_id and query.equal_points == 1 and query.sentry is None:
        #     winner = dev_name
        #     session.query(Team).filter(Team.id == dev_id).update({'sentry': 1}, False)
        #     session.commit()
        #     flag = True
        #     break


def run():
    """
    Если дата сейчас не совпадает с выходными и праздниками то работаем
    """
    if datetime.now().strftime("%d.%m.%y") in holidays \
            or datetime.now().strftime("%A") in day_off:
        exit('Holiday')
    else:
        update_all_issues()
        dev_points = session.query(Team).order_by(Team.total.desc())
        total_all_team = session.query(func.sum(Team.total)).scalar()
        all_developer = session.query(Team.id).count()
        average = ceil(total_all_team / all_developer)

        update_equal_points(dev_points)

        # исключить повторения одного человека
        sum_equal_points = session.query(func.sum(Team.equal_points)).filter(Team.equal_points == EnumEqualPoints.orderly).scalar()
        sum_sentrys = session.query(func.sum(Team.sentry)).filter(Team.equal_points == EnumEqualPoints.orderly).scalar()

        # Выбор счасливчика с наименьшим кол-вом поинтов
        querys = session.query(Team).all()
        winner = choose_developer(querys, sum_equal_points, sum_sentrys)

        text_strings = [
            u'*Поздравляем!* :tada: {} сегодня дежурный по багам :bug:'.format(winner),
            u'_Поинты команды = {}_'.format(total_all_team),
            u'_Среднее кол-во поинтов команды = {}_'.format(int(average))
        ]

        team_points = session.query(Team).order_by(Team.total.desc())
        for point in team_points:
            developer_vacation = ''
            if point.equal_points == 2:
                developer_vacation = u'Отпуск/Отгул'
            elif point.equal_points == 3:
                developer_vacation = u'Преподает'
            text_strings.append('<{url}|{name}> = {point}  {vacation}'.format(
                url=point.jira_url,
                name=point.name,
                point=point.total,
                vacation=developer_vacation if developer_vacation else ''))
        # TODO ссылка на гифку не раскрывается
        # text_strings.append('\n{}'.format(get_random_cat()))

        return '\n'.join(text_strings)


if __name__ == '__main__':

    run()
