import uuid as uuid
from django.contrib.auth.models import AbstractUser
from django.db import models




class PollUser(AbstractUser):

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


class Poll(models.Model):

    class Meta:
        verbose_name = 'Опрос'
        verbose_name_plural = 'Опросы'

    name = models.CharField(max_length=100, verbose_name='Название опроса')
    start_date = models.DateField(verbose_name='Начало опроса', auto_now_add=True, editable=False)
    end_date = models.DateField(verbose_name='Окончание опроса')
    description = models.TextField(verbose_name='Описание', blank=True, null=True)

    def __str__(self):
        return self.name


class Question(models.Model):

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        unique_together = ('number', 'poll')

    TYPE_CHOICES = (
        ('TEXT', 'Текст'),
        ('ONE CHOICE', 'Один вариант ответа'),
        ('MULTIPLE CHOICES', 'Несколько вариантов ответа')
    )

    poll = models.ForeignKey('polls.Poll', on_delete=models.CASCADE, related_name='questions', verbose_name='Опрос')
    number = models.IntegerField(verbose_name='Номер вопроса')
    text = models.TextField(verbose_name='Описание')
    answer_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Тип ответа')

    def save(self, **kwargs):
        if self.answer_type == 'TEXT' and self.answer_choices.exists():
            raise ValueError('Вопрос с атрибутом answer type, равным "TEXT", не может иметь вариантов ответа')
        return super().save(**kwargs)

    def __str__(self):
        return self.text


class AnswerChoice(models.Model):

    class Meta:
        verbose_name = 'Варианты ответ на вопрос',
        verbose_name_plural = 'Варианты ответа на вопрос'
        unique_together = ('question', 'text')

    question = models.ForeignKey('polls.Question', on_delete=models.CASCADE, related_name='answer_choices',
                                 verbose_name='Вопрос')
    text = models.CharField(max_length=100, verbose_name='Ответ')

    def __str__(self):
        return f'Вариант ответа на вопрос {self.question.text}'


class CompletedPoll(models.Model):

    class Meta:
        verbose_name = 'Пройденный опрос'
        verbose_name_plural = 'Пройденные опросы'
        unique_together = ('user', 'poll')

    poll = models.ForeignKey('polls.Poll', on_delete=models.CASCADE, related_name='completed', verbose_name='Опрос')
    user = models.ForeignKey('polls.PollUser', on_delete=models.CASCADE, to_field='uuid', related_name='completed_polls',
                             verbose_name='Пользователь')
    answers = models.TextField(verbose_name='Ответы пользователя')
    # JSONField появился в версии 3.1 - приходится использовать TextField

    def __str__(self):
        return f'Ответы пользователя {self.user} на опрос {self.poll.name}'



