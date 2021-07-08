import json
from datetime import date

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from polls.models import Poll, Question, AnswerChoice, CompletedPoll, PollUser


class AnswerChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerChoice
        fields = ('text',)


class AnswerChoiceInCompletedPollSerializer(serializers.Serializer):
    """
    Если ответ один - записывается в text
    Если ответов несколько - в text_list
    """
    question = serializers.IntegerField(min_value=1)
    text = serializers.CharField(allow_blank=True)
    text_list = serializers.ListField(child=serializers.CharField(), allow_empty=True)

    class Meta:
        model = AnswerChoice
        fields = ('question', 'text', 'text_list')

    def create(self, validated_data):
        return

    def update(self, instance, validated_data):
        return


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


class CompletedPollCreateSerializer(serializers.ModelSerializer):
    answers = AnswerChoiceInCompletedPollSerializer(many=True)

    class Meta:
        model = CompletedPoll
        fields = ('poll', 'answers')

    def validate(self, data):
        poll = data.get('poll')
        validated_data = {'poll': data.get('poll')}
        answers = []

        for answer in data.get('answers'):
            try:
                question = Question.objects.get(number=answer.get('question'), poll=poll)
            except Question.DoesNotExist:
                raise ValidationError(f'Вопроса под номером {answer.get("question")} не существует в опросе {poll.name}')
            if question.answer_type == 'TEXT' and answer.get('text') is None:
                raise ValidationError(f'Требуется ответ на вопрос "{question.text}"')
            if question.answer_type == 'ONE CHOICE' and answer.get('text') not in \
                    AnswerChoice.objects.filter(question=question).values_list('text', flat=True):
                raise ValidationError(f'Данного варианта ответа не существует ({answer.get("text")})')
            not_valid_answers = set(answer.get('text_list', [])) - \
                                set(AnswerChoice.objects.filter(question=question).values_list('text', flat=True))
            if question.answer_type == 'MULTIPLE CHOICE' and not_valid_answers:
                raise ValidationError(f'Данных вариантов ответа не существует ({",".join(not_valid_answers)})')
            answers.append({'question': question.text,
                            'text': answer.get('text', ''),
                            'text_list': answer.get('text_list', [])})

        validated_data['answers'] = json.dumps(answers)
        return validated_data


class CompletedPollListSerializer(serializers.ModelSerializer):
    poll = serializers.CharField(source='poll.name', default='-')
    answers = serializers.SerializerMethodField()

    class Meta:
        model = CompletedPoll
        fields = ('poll', 'answers')

    def get_answers(self, instance: CompletedPoll):
        return json.loads(instance.answers)


class PollUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollUser
        fields = ('uuid',)


class PollUserDetailSerializer(serializers.ModelSerializer):
    completed_polls = CompletedPollListSerializer(many=True)

    class Meta:
        model = PollUser
        fields = ('uuid', 'completed_polls')


"""
{
    "poll": 4,
    "answers": [
    {"question": 1, "text": "DENIS", "text_list": []},
    {"question": 2, "text":"18-25", "text_list": []},
    {"question": 3, "text": "", "text_list": ["Война и мир", "Анна Каренина"]}
]
}
"""
