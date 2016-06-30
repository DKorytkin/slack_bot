#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Denis'

from datetime import datetime
from math import ceil

import requests
from models import session, Team

from parse_data import elapsed_time_task_in_seconds, get_issues_histories, get_existing_issues

CAT_ENDPOINT = "http://random.cat/meow"
DEFAULT_CAT = "http://media.topito.com/wp-content/uploads/2013/01/code-12.gif"

# Список праздников, не рабочих дней
holidays = [
    '01.01.16', '07.01.16',
    '08.03.16',
    '01.05.16', '03.05.16', '09.05.16',
    '20.06.16', '28.06.16',
    '24.08.16',
    '14.10.16'
]

# Список выходных
day_off = ['Saturday', 'Sunday']


def get_random_cat():
    r = requests.get(CAT_ENDPOINT)
    try:
        url = r.json()['file']
    except:
        url = DEFAULT_CAT
    return url


def run():
    """
    Если дата сейчас не совпадает с выходными и прзадниками то работаем
    equal_points:
    1 = Одинаковое кол-во поинтов
    2 = Отпуск
    3 = Макс преподает
    """
    if datetime.now().strftime("%d.%m.%y") in holidays \
            or datetime.now().strftime("%A") in day_off:
        exit('Holiday')
    else:
        values_in_db = session.query(Team).all()
        total_all_team, all_developer = 0, 0
        all_team = []
        for value in values_in_db:
            # Общие поинты
            total_all_team += value.total
            # Количество девелоперов
            all_developer += 1
            # Проверка в четверг для Макса Thursday
            if datetime.now().strftime('%A') == 'Thursday' and value.id == 3:
                session.query(Team).filter(Team.id == value.id).update({'equal_points': 3}, False)
            # Проверка отпуска
            elif value.date_start is None:
                list_team = [value.id, value.name, value.total]
                all_team.append(list_team)
                session.query(Team).filter(Team.id == value.id).update({'equal_points': None}, False)
                continue
            elif value.date_start <= datetime.now().date() <= value.date_over:
                session.query(Team).filter(Team.id == value.id).update({'equal_points': 2}, False)
            else:
                list_team = [value.id, value.name, value.total]
                all_team.append(list_team)
                session.query(Team).filter(Team.id == value.id).update({'equal_points': None}, False)
            session.commit()

        # среднее по поинтам среди команды
        average = ceil(total_all_team / all_developer)

        # Сортировка по второму значению(total)
        all_team.sort(key=lambda x: x[2])

        # исключить повторения одного человека
        for point in all_team:
            if point[2] == all_team[0][2]:
                session.query(Team).filter(Team.id == point[0]).update({'equal_points': 1}, False)
            else:
                session.query(Team).filter(Team.id == point[0]).update({'equal_points': None}, False)
            session.commit()

        equal_points = 0
        sentrys = 0
        count_equal_points_and_sentrys = session.query(Team).all()
        for query in count_equal_points_and_sentrys:
            if query.equal_points == 1:
                equal_points += 1
            if query.sentry == 1:
                sentrys += 1

        # Выбор счасливчика с наименьшим кол-вом поинтов
        winner = []
        flag = False
        querys = session.query(Team).all()
        # TODO
        # переделать, черт ногу сломит
        for query in querys:
            for one in all_team:
                if one[2] <= average:
                    if query.id == one[0] and query.equal_points == 1 and equal_points <= sentrys:
                        winner = one[1]
                        session.query(Team).update({'sentry': None}, False)
                        session.commit()
                        session.query(Team).filter(Team.id == one[0]).update({'sentry': 1}, False)
                        session.commit()
                        flag = True
                        break
                    elif query.id == one[0] and query.equal_points == 1 and query.sentry is None:
                        winner = one[1]
                        session.query(Team).filter(Team.id == one[0]).update({'sentry': 1}, False)
                        session.commit()
                        flag = True
                        break
            if flag:
                break
        text_strings = [
            "*Поздравляем!* :tada: {} сегодня дежурный по багам :bug:".format(winner),
            "_Поинты команды = {}_".format(total_all_team),
            "_Среднее кол-во поинтов команды = {}_".format(int(average))
        ]

        team_points = session.query(Team).all()
        for point in team_points:
            developer_vacation = ''
            if point.equal_points == 2:
                developer_vacation = 'Отпуск/Отгул'
            elif point.equal_points == 3:
                developer_vacation = 'Преподает'
            text_strings.append('<{url}|{name}> = {point}  {vacation}'.format(
                url=point.jira_url,
                name=point.name,
                point=point.total,
                vacation=developer_vacation if developer_vacation else ''))
        # TODO
        # ссылка на гифку не раскрывается
        # text_strings.append('\n{}'.format(get_random_cat()))

        return '\n'.join(text_strings)


if __name__ == '__main__':
    elapsed_time_task_in_seconds(get_existing_issues())

    get_issues_histories(get_existing_issues())

    run()
