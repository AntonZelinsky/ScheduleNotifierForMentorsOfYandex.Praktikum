import datetime
import logging

from app.schemas import DutyPageCreate
from core.models import Cohort
from core.notion_integration import NotionClient
from helpers import Expando, plural


class NotionServices:
    """
    Services class, contains all functionality for receiving and processing data from Notion API
    """
    client = NotionClient()

    def get_mentors_on_duty(self, cohorts: list[Cohort]) -> dict:
        """
        Returns a dict of all on-duty mentors and their cohorts for today.
        Example: {mentor@email.here: [cohort1, cohort2]}
        """
        mentors_on_duty = dict()
        for notion_database in cohorts:
            response = self.client.get_cohort_schedule_from_notion(notion_database)

            for item in response.results:
                properties = item.properties
                user_data = Expando()
                user_data.database = notion_database

                user_data.email = properties.Дежурный.people[0].person.email
                if user_data.email in mentors_on_duty:
                    mentors_on_duty[user_data.email].append(user_data.database)
                else:
                    mentors_on_duty[user_data.email] = [user_data.database]

        return mentors_on_duty

    def generate_schedule(self, cohort: Cohort, max_days: int = 14):
        """
        Генерировать расписание для когорты
        :param cohort: когорта
        :param max_days: кол-во дней добавляемых к расписанию,
        :return: список добавленных ноушен страниц
        """

        last_duties = self.get_last_duties_by_cohort(cohort)
        if not last_duties:
            return False

        need_days = datetime.date.today() + datetime.timedelta(days=max_days) - last_duties['actual_date']
        need_days = need_days.days
        if need_days < 1:
            logging.info(f'Когорта "{cohort.name}" не нуждается в продлении расписания. '
                         'Похоже, оно уже заполнено как минимум '
                         f'на {max_days} {plural(max_days, ["день", "дня", "дней"])} вперед.')
            return False

        cycle = self.find_cycle_by_last_duties(last_duties['last_mentors'])
        timeline = self.make_timeline(cycle, last_duties['actual_date'], need_days)

        added = []
        for duty in timeline:
            added_page_id = self.client.create_duty_page(DutyPageCreate(
                database_id=cohort.notion_db_id,
                date=duty['date'],
                mentor_name=duty['mentor']['name'],
                notion_user_id=duty['mentor']['id'],
            ))
            added.append(added_page_id)

        logging.info(f'В {cohort.name} продлено расписание '
                     f'на {len(added)} {plural(len(added), ["день", "дня", "дней"])}.')

    def get_last_duties_by_cohort(self, cohort: Cohort, count_days: int = 7) -> dict:
        """
        Получить последовательность из `:count` крайних дежурств в обратном порядке.
        Данные из прошлого не учитываем.
        :param cohort: когорта,
        :param count_days: количество дней для расчета,
        :return:
            {
                'last_mentors_ids': tuple, крайние дежурства. **Порядок обратный --** от последнего к первому.
                'actual_date': date(%Y-%m-%d), крайняя заполненная дата (%Y-%m-%d)
            }
        """
        date_now = datetime.date.today().__str__()
        databases_duties = self.client.query_databases_duties(
            database_id=cohort.notion_db_id,
            date=date_now,
            page_size=count_days,
        )

        if len(databases_duties) < 2:
            logging.error('Недостаточно данных для расчета расписания. Нужен минимум один цикл дежурств в будущем.')
            return False
        last_duties = [duty.properties for duty in databases_duties]
        last_duties = sorted(last_duties, key=lambda duty: duty.Дата.date.start, reverse=True)
        actual_date = datetime.datetime.strptime(last_duties[0].Дата.date.start, '%Y-%m-%d').date()
        last_mentors_ids = tuple(dict(
            id=duty.Дежурный.people[0].id,
            name=duty.Дежурный.people[0].name
        ) for duty in last_duties)
        last_mentors = {
            "last_mentors": last_mentors_ids,
            "actual_date": actual_date
        }

        return last_mentors

    def find_cycle_by_last_duties(self, last_duties: tuple) -> tuple:
        """
        Получить цикл дежурств наставников из последовательности крайних дежурств.
        Подразумеваем, что цикл точно есть, минимум 1.
        Что последовательность из элементов по одному.
        Последовательность дана **в обратном порядке.**
        :return: tuple. Вернуть **в прямом порядке.**
        """
        cycle = []
        for i, mentor in enumerate(last_duties):
            if mentor in cycle:
                break
            cycle.insert(i, mentor)
        return tuple(reversed(cycle))

    def make_timeline(self, cycle: tuple, start_date: str, set_period: int) -> list:
        """
        Сделать список-таймлайн. В списке на каждую дату назначен наставник.
        :param cycle: цикл дежурств,
        :param start_date: крайняя дата заполненного расписания,
        :param set_period: кол-во дней добавляемых к расписанию,
        :return: Список расписание на :set_interval дней, от :start_date + 1. На каждую дату назначен наставник.
        """
        future_duties = [None] * set_period
        duty_date = start_date
        for i in range(set_period):
            duty_date += datetime.timedelta(days=1)
            mentor = cycle[i % len(cycle)]
            future_duties[i] = dict(mentor=mentor, date=duty_date)

        return future_duties
