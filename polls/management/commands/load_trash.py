from datetime import date, timedelta

from django.core.management.base import BaseCommand

from polls.models import PollUser, Poll, Question, AnswerChoice


class Command(BaseCommand):
    help = 'Load trash to DB'

    def handle(self, *args, **options):
        print('Start loading trash')

        users = {
            'admin': 'admin',
            'Jack': 'JackPassword',
            'David': 'DavidPassword',
            'Julia': 'JuliaPassword'
        }
        for login, password in users.items():
            try:
                PollUser.objects.get(username=login)
                continue
            except PollUser.DoesNotExist:
                pass
            PollUser.objects.create_user(login, password=password) \
                if login != 'admin' \
                else PollUser.objects.create_superuser(login, email='', password=password)

        polls = [
            {
                'name': 'Первый опрос',
                'description': 'Описание первого опроса',
                'end_date': date.today() + timedelta(days=7),
                'questions': [
                    {
                        'text': 'Как вас зовут?',
                        'answer_type': 'TEXT',
                    },
                    {
                        'text': 'Сколько вам лет?',
                        'answer_type': 'ONE_CHOICE',
                        'answer_choices': [
                            {'text': '<18'},
                            {'text': '18-25'},
                            {'text': '25-40'},
                            {'text': '40+'},
                        ]
                    },
                    {
                        'text': 'Какие из предложенных книг вам интересны',
                        'answer_type': 'MULTIPLE_CHOICES',
                        'answer_choices': [
                            {'text': 'Война и мир'},
                            {'text': 'Преступление и наказание'},
                            {'text': 'Анна Каренина'},
                            {'text': 'Мастер и Маргарита'},
                            {'text': 'Американская трагедия'},
                            {'text': 'Кафка на пляже'},
                        ]
                    }
                ]
            },
            {
                'name': 'Второй опрос',
                'description': 'Описание второго опроса',
                'end_date': date.today() + timedelta(days=10),
                'questions': [
                    {
                        'text': 'Опишите ваше самочувствие',
                        'answer_type': 'TEXT',
                    },
                    {
                        'text': 'Сколько вам лет?',
                        'answer_type': 'ONE_CHOICE',
                        'answer_choices': [
                            {'text': '<18'},
                            {'text': '18-25'},
                            {'text': '25-40'},
                            {'text': '40+'},
                        ]
                    },
                    {
                        'text': 'Какие из предложенных фильмов вам интересны?',
                        'answer_type': 'MULTIPLE_CHOICES',
                        'answer_choices': [
                            {'text': 'Терминатор'},
                            {'text': 'Таксист'},
                            {'text': 'Амели'},
                            {'text': 'Драйв'},
                            {'text': 'На игле'},
                            {'text': 'Вечное сияние чистого разума'},
                        ]
                    }
                ]
            },
            {
                'name': 'Неактуальный опрос',
                'description': 'Описание неактуального опроса',
                'end_date': date.today() - timedelta(days=2),
                'questions': [
                    {
                        'text': 'Что вы ели сегодня на завтрак?',
                        'answer_type': 'TEXT',
                    },
                    {
                        'text': 'Какую оценку вы бы хотели получить на уроке?',
                        'answer_type': 'ONE_CHOICE',
                        'answer_choices': [
                            {'text': '2'},
                            {'text': '3'},
                            {'text': '4'},
                            {'text': '5'},
                        ]
                    },
                ]
            }
        ]
        for poll_data in polls:
            try:
                poll = Poll.objects.get(name=poll_data.get('name'), description=poll_data.get('description'))
                poll.end_date = poll_data.get('end_date')
            except Poll.DoesNotExist:
                poll = Poll.objects.create(name=poll_data.get('name'), description=poll_data.get('description'),
                                           end_date=poll_data.get('end_date'))
            for i, question_data in enumerate(poll_data.get('questions')):
                question = Question.objects.get_or_create(text=question_data.get('text'), number=i + 1,
                                                          answer_type=question_data.get('answer_type'),
                                                          poll=poll)[0]
                for answer_choice_data in question_data.get('answer_choices', []):
                    AnswerChoice.objects.get_or_create(text=answer_choice_data.get('text'), question=question)
                question.save()
            poll.save()

        print('End loading trash')


