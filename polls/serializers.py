import json
from datetime import date

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from polls.models import Poll, Question, AnswerChoice, CompletedPoll, PollUser


class AnswerChoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnswerChoice
        fields = ('text', )


class QuestionCreateUpdateSerializer(serializers.ModelSerializer):
    answer_choices = AnswerChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ('poll', 'text', 'answer_type', 'answer_choices')


class QuestionDetailSerializer(serializers.ModelSerializer):
    answer_choices = AnswerChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ('poll', 'number', 'text', 'answer_type', 'answer_choices')


class PollDetailSerializer(serializers.ModelSerializer):
    questions = QuestionDetailSerializer(many=True)

    class Meta:
        model = Poll
        fields = ('name', 'start_date', 'end_date', 'description', 'questions')


class PollListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Poll
        fields = ('name', 'start_date', 'end_date', 'description')


class PollCreateUpdateSerializer(serializers.ModelSerializer):
    questions = QuestionCreateUpdateSerializer(many=True)

    class Meta:
        model = Poll
        fields = ('name', 'end_date', 'questions', 'description')

    def validate(self, data):
        if Poll.objects.filter(name=data.get('name')).exists():
            raise ValidationError(f'Опрос с названием {data.get("name")} уже существует')
        if data.get('end_date') < date.today():
            raise ValidationError(f'Дата окончания опроса не может находиться в прошлом')
        for question_data in data.get('questions'):
            if not (question_data.get('text') or question_data.get('answer_type')):
                raise ValidationError(f'У вопроса указаны не все необходимые поля')
            if question_data.get('answer_type') not in [x[0] for x in Question.TYPE_CHOICES]:
                raise ValidationError(f'Вопрос не может быть типа {question_data.get("answer_type")}')
            if question_data.get('answer_type') in ('ONE CHOICE', 'MULTIPLE CHOICES') \
                    and not question_data.get('answer_choices'):
                raise ValidationError('Вопрос с выбором варианта/ов ответа должен содержать хотя бы один ответ')
            if question_data.get('answer_type') != 'TEXT':
                for answer_choice in question_data.get('answer_choices'):
                    if not answer_choice.get('text'):
                        raise ValidationError('Сущность ответа должна содержать атрибут text')
        return data


class CompletedPollSerializer(serializers.ModelSerializer):
    poll = serializers.CharField(source='poll.name', default='-')
    answers = serializers.SerializerMethodField()

    class Meta:
        model = CompletedPoll
        fields = ('poll_name', 'answers')

    def get_answers(self, instance: CompletedPoll):
        return json.loads(instance.answers)


class PollUserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = PollUser
        fields = ('uuid', )


class PollUserDetailSerializer(serializers.ModelSerializer):
    completed_polls = CompletedPollSerializer(many=True)

    class Meta:
        model = PollUser
        fields = ('uuid', 'completed_polls')
