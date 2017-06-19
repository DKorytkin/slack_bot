#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'Denis'

from math import ceil
import requests

from sqlalchemy import func
from sqlalchemy import desc

from models import session, Team, EnumStatus
from objects import CAT_ENDPOINT, DEFAULT_CAT
from parse_data import update_status, choose_developer


equal_type = EnumStatus


def get_random_cat():
    r = requests.get(CAT_ENDPOINT)
    try:
        url = r.json()['file']
    except:
        url = DEFAULT_CAT
    return url


def run():

    # update_all_issues()
    dev_points = session.query(Team).order_by(Team.total.desc())
    total_all_team = session.query(func.sum(Team.total)).scalar()
    all_developer = session.query(Team.id).count()
    average = ceil(total_all_team / all_developer)

    update_status(dev_points)

    # исключить повторения одного человека
    sum_equal_points = session.query(func.sum(Team.status)).filter(
        Team.status == EnumStatus.orderly
    ).scalar()
    sum_sentrys = session.query(func.sum(Team.sentry)).filter(
        Team.status == EnumStatus.orderly
    ).scalar()

    # Выбор счасливчика с наименьшим кол-вом поинтов
    querys = session.query(Team).all()
    winner = choose_developer(querys, sum_equal_points, sum_sentrys)

    text_strings = [
        u'*Поздравляем!* :tada: {} сегодня дежурный по багам :bug:'.format(
            winner
        ),
        u'_Поинты команды = {}_'.format(total_all_team),
        u'_Среднее кол-во поинтов команды = {}_'.format(int(average))
    ]
    team_points = session.query(
        (Team.total + Team.vacation_boost).label('all'),
        Team.total,
        Team.vacation_boost,
        Team.name,
        Team.status,
        Team.jira_url
    ).order_by(desc('all')).all()

    for point in team_points:
        developer_vacation = ''
        if point.status == EnumStatus.vacation:
            developer_vacation = u'Отпуск/Отгул'
        elif point.status == EnumStatus.teaching:
            developer_vacation = u'Преподает'
        text_strings.append('<{url}|{name}> = {point}  {vacation}'.format(
            url=point.jira_url,
            name=point.name,
            point=point.all,
            vacation=developer_vacation if developer_vacation else ''
        ))
    # TODO ссылка на гифку не раскрывается
    #text_strings.append('\n{}'.format(get_random_cat()))

    return '\n'.join(text_strings)


if __name__ == '__main__':
    run()
