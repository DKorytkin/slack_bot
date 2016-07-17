#!/usr/bin/env python3
# coding: utf-8
__author__ = 'Denis'

from collections import namedtuple
from datetime import datetime, date

import xlrd

from models import All_bugs, Team, session
from objects import jira

Vacations = namedtuple('Vacations', ['ids', 'date_start', 'date_over'])
Issue = namedtuple("Issue", ["title", "priority", "summary", "date_created", "date_resolution", "developer"])

TEAM = {
    u'Виталий Харитонский': 1,
    u'Дмитрий Наконечный': 2,
    u'Максим Краковян': 3,
    u'Андрей Кушнир': 4,
    u'Игорь Топал': 5,
    u'Александр Танкеев': 6,
}

FILE_VACATIONS = 'dev_vacations.xls'


# сделать проверку по времени, для разных кварталов
def get_issues_filter():
    """
    в зависимости какая сегодня дата выбирает квартал и подставляет даты в фильтр
    """

    issues_filter = (
        'project = PR AND '
        'issuetype = Bug AND'
        ' created >= 2016-01-01 AND'
        ' Developer in ("d.nakonechny", "a.tankeev", "a.kushnir", "v.haritonskiy", "m.krakovyan", "i.topal")'
    )

    return issues_filter


def get_issues(filter):
    name_issues = jira.search_issues(filter, maxResults=None)
    for issue in name_issues:
        title = issue.key
        summary = issue.fields.summary
        priority = issue.fields.priority.name
        date_created = issue.fields.created
        date_resolution = issue.fields.resolutiondate
        developer = issue.fields.customfield_10391.displayName
        yield Issue(
            title=title,
            priority=priority,
            summary=summary,
            date_created=date_created,
            date_resolution=date_resolution,
            developer=developer
        )


def insert_tasks(issues, existing_issue_names):
    """
        Записывает в БД только новые данные по таскам: Название, Приоритет, Описание, Девелопера
        пример: PR-666, Major, Error on main page, i.topal, foreignKey=Team.id
        issues=парсин с jira
        existing_issue_names=выборка с БД по названию таски, проверка на повторение
    """
    for issue in issues:
        if issue.title in existing_issue_names:
            continue
        developer_id = TEAM[issue.developer]
        # Парсинг даты создания и закрытия таски
        if issue.date_created is not None:
            date_create = format_date(issue.date_created)

        bugs = All_bugs(
            task_name=issue.title,
            priority=issue.priority,
            description=issue.summary,
            developer_name=issue.developer,
            date_created=date_create if date_create else None,
            date_resolution=None,
            ready_for_dev=None,
            in_dev=None,
            ready_for_test=None,
            elapsed_time_for_task_in_hours=None,
            developer_id=developer_id,
        )
        session.add(bugs)
    session.commit()


def get_existing_issues():
    all_existing_issues = session.query(All_bugs).all()
    return all_existing_issues


def format_date(date):
    return datetime.strptime((date[0:19].replace('T', ' ')), '%Y-%m-%d %H:%M:%S')


def update_issue_date_resolution(issues, existing_issue_names):
    """
    Обновление даты резолюции
    """
    for issue in issues:
        for title in existing_issue_names:
            if issue.title == title:
                # Парсинг даты закрытия таски
                if issue.date_resolution is not None:
                    date_resolution = format_date(issue.date_resolution)
                    session.query(All_bugs).filter(All_bugs.task_name == title) \
                        .update({'date_resolution': date_resolution if date_resolution else None}, False)
            else:
                continue

        session.commit()


def update_issues_from_histories(all_issues):
    """
    Достает из истории изменений время смены статусов
    assignee to developer, in dev, ready for test
    """

    def is_assignee_history(history):
        return bool(
            [item for item in history.items if item.field == 'assignee']
        )

    def is_status_history(history):
        return bool(
            [item for item in history.items if item.field == 'status']
        )

    for issue in all_issues:
        ready_for_dev = None
        in_dev = None
        ready_for_test = None
        date_assignee = []
        date_ready_for_dev = []
        date_in_dev = []
        date_ready_for_test = []

        jira_issue = jira.issue(issue.task_name, expand='changelog')
        changelog_issue = jira_issue.changelog
        for history in changelog_issue.histories:
            if not is_status_history(history) and not is_assignee_history(history):
                continue

            for item in history.items:
                if item.toString == issue.developer_name:
                    date_assignee.append(history.created)
                    if date_assignee:
                        ready_for_dev = format_date(date_assignee[0])

                # Если в таске нет assignee использовать Ready for dev таска при создании была назначена на Developer
                # Или елси assignee не первый в items значит одновременно был assignee и ready for dev
                if item.toString == 'Ready for dev':
                    date_ready_for_dev.append(history.created)
                    if not date_assignee:
                        ready_for_dev = format_date(date_ready_for_dev[0])

                if history.author.displayName == issue.developer_name and item.toString == 'In dev':
                    date_in_dev.append(history.created)
                    if date_in_dev:
                        in_dev = format_date(date_in_dev[0])

                if item.toString == 'Ready for test':
                    date_ready_for_test.append(history.created)
                    if date_ready_for_test:
                        ready_for_test = format_date(date_ready_for_test[-1])

        session.query(All_bugs).filter(All_bugs.task_name == issue.task_name).update({
            'ready_for_dev': ready_for_dev if ready_for_dev else None,
            'in_dev': in_dev if in_dev else None,
            'ready_for_test': ready_for_test if ready_for_test else None
        }, False)
        session.commit()


def elapsed_time_task_in_seconds(all_tasks):
    """
    Заполняет затраченое время на багу в секундах
    """
    for elapsed_time_for_task in all_tasks:
        if elapsed_time_for_task.in_dev is not None and elapsed_time_for_task.ready_for_test is not None:
            time_for_task = elapsed_time_for_task.ready_for_test - elapsed_time_for_task.in_dev
            elapsed_time = (24 * 3600 * time_for_task.days if time_for_task.days else 0) + time_for_task.seconds
            session.query(All_bugs).filter(All_bugs.id == elapsed_time_for_task.id).update({
                'elapsed_time_for_task_in_seconds': elapsed_time
            }, False)
    session.commit()


# Parse data from Team table
def parsing_vacation(file):
    """
    Выбирает с файла dev_vacations.xls дату начала и окончания отпуска
    file.xls
    """
    def format_date_xls(date):
        date_tuple = xlrd.xldate_as_tuple(date, 0)
        return datetime(*date_tuple).date()

    team_vacations = []

    workbook = xlrd.open_workbook(file)
    sheet = workbook.sheet_by_index(0)
    for row in range(1, sheet.nrows):
        developers_vacation = [sheet.cell_value(row, col) for col in range(0, sheet.ncols)]
        id_dev = developers_vacation[0]
        date_start_vacation = format_date_xls(developers_vacation[2]) if developers_vacation[2] else None
        date_over_vacation = format_date_xls(developers_vacation[3]) if developers_vacation[3] else None
        team = (Vacations(ids=id_dev, date_start=date_start_vacation, date_over=date_over_vacation))
        team_vacations.append(team)
    return team_vacations


def insert_developers(team, dev_name_overlap):
    """
    добавление в Team девелоперов
    team=список команды
    dev_name_overlap=проверка на совпадение в базе
    """
    for dev in team:
        developer_id = TEAM[dev]
        if dev in dev_name_overlap:
            continue
        else:
            name = Team(developer_id, None, None, None, None, None, None, dev, None, None, None, None, None)
            session.add(name)
    session.commit()


def update_developers(issues, get_existing_issues):
    """
    Update developers(foreign key) in All_bugs
    """
    for existing_issue in get_existing_issues:
        for issue in issues:
            developer_id = TEAM[issue.developer]
            if issue.title == existing_issue.task_name and issue.developer == existing_issue.developer_name:
                continue
            session.query(All_bugs).filter(All_bugs.task_name == issue.title).update(dict(
                priority=issue.priority,
                developer_name=issue.developer,
                developer_id=developer_id
            ), False)

    session.commit()


def update_developers_vacations(developer_vacations):
    """
    Обновляет поля начало и конец отпуска в Team из файла
    """
    for vacations in developer_vacations:
        if vacations.date_start is not None:
            date_start_vacation = vacations.date_start
            date_over_vacations = vacations.date_over
        else:
            date_start_vacation = None
            date_over_vacations = None
        session.query(Team).filter(Team.id == vacations.ids).update({
            'date_start': date_start_vacation,
            'date_over': date_over_vacations
        }, False)

        session.commit()


def mario_update_developers_vacations(vacation_data):
    """
    Mario обновляет поля начало и конец отпуска в Team
    """
    def is_date(date):
        try:
            return datetime.strptime(date, '%d-%m-%Y')
        except ValueError:
            return datetime.strptime(date, '%d-%m-%y')

    developers = session.query(Team.id, Team.name).all()
    for developer in developers:
        # TODO add list names for developer and check in
        if vacation_data.dev_name in developer.name.lower():
            session.query(Team).filter(Team.id == developer.id).update({
                'date_start': is_date(vacation_data.date_start).date(),
                'date_over': is_date(vacation_data.date_over).date()
            }, False)
    session.commit()


def update_team_bugs(team_ids, all_bugs):
    """
    Обновление Team, заполняются сумма багов по приоритету
    """
    blocker, critical, major, minor, trivial = 0, 0, 0, 0, 0
    for bug in all_bugs:
        if bug.priority == 'Blocker' and bug.developer_id == team_ids:
            blocker += 5
        elif bug.priority == 'Critical' and bug.developer_id == team_ids:
            critical += 4
        elif bug.priority == 'Major' and bug.developer_id == team_ids:
            major += 3
        elif bug.priority == 'Minor' and bug.developer_id == team_ids:
            minor += 2
        elif bug.priority == 'Trivial' and bug.developer_id == team_ids:
            trivial += 1
    count = [team_ids, blocker, critical, major, minor, trivial]
    session.query(Team).filter(Team.id == count[0]).update({
        'blocker': count[1],
        'critical': count[2],
        'major': count[3],
        'minor': count[4],
        'trivial': count[5]
    }, False)
    session.commit()


def update_total_team_bugs():
    team_bugs = session.query(Team.id, (Team.blocker + Team.critical + Team.major + Team.minor + Team.trivial).label('sum')).all()
    for team_bug in team_bugs:
        session.query(Team).filter(Team.id == team_bug.id).update({'total': team_bug.sum}, False)
    session.commit()


def update_all_issues():
    tasks = session.query(All_bugs.task_name).all()
    query_task_name = [task.task_name for task in tasks]
    # insert new tasks
    insert_tasks(get_issues(get_issues_filter()), query_task_name)
    # update foreign key (change developer)
    update_developers(get_issues(get_issues_filter()), get_existing_issues())

    # insert developers
    developers = session.query(Team.name).all()
    dev_names = [developer.name for developer in developers]
    insert_developers(TEAM, dev_names)

    # update vacation from file.xls
    update_developers_vacations(parsing_vacation(FILE_VACATIONS))
    # update bug points
    team_ids = session.query(Team.id).all()
    for developer in team_ids:
        update_team_bugs(developer.id, get_existing_issues())
    update_total_team_bugs()

    update_issue_date_resolution(get_issues(get_issues_filter()), query_task_name)

    elapsed_time_task_in_seconds(get_existing_issues())

    update_issues_from_histories(get_existing_issues())
    # TODO add update type issue (bug to task)!!!

if __name__ == '__main__':
    update_all_issues()
