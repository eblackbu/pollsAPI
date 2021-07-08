import copy

from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from polls.filters import PollFilter, QuestionFilter
from polls.models import Poll, Question, PollUser, CompletedPoll, AnswerChoice
from polls.serializers import PollListSerializer, PollDetailSerializer, QuestionDetailSerializer, \
    PollCreateUpdateSerializer, CompletedPollListSerializer, PollUserListSerializer, PollUserDetailSerializer, \
    QuestionCreateUpdateSerializer, CompletedPollCreateSerializer


class PollViewSet(CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, ListModelMixin, viewsets.GenericViewSet):
    queryset = Poll.objects.all()
    serializer_mapping = {
        'list': PollListSerializer,
        'retrieve': PollDetailSerializer,
        'create': PollCreateUpdateSerializer
    }
    permission_classes = {
        'create': (IsAdminUser, ),
    }
    filterset_class = PollFilter

    def get_serializer_class(self):
        return self.serializer_mapping.get(self.action, PollListSerializer)

    def get_permissions(self):
        return [perm() for perm in self.permission_classes.get(self.action, [])]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        with transaction.atomic():
            poll = Poll.objects.create(name=validated_data.get('name'), end_date=validated_data.get('end_date'),
                                       description=validated_data.get('description'))
            for i, question_data in enumerate(validated_data.get('questions')):
                question = Question.objects.create(poll=poll, number=i + 1, text=question_data.get('text'),
                                                   type=question_data.get('type'))
                for answer_choice_data in question_data.get('answer_choices'):
                    AnswerChoice.objects.create(text=answer_choice_data.get('text'), question=question)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=self.get_success_headers(serializer.data))


class QuestionViewSet(CreateModelMixin, UpdateModelMixin, ListModelMixin, viewsets.GenericViewSet):
    queryset = Question.objects.all().select_related('poll')
    serializer_mapping = {
        'list': QuestionDetailSerializer,
        'retrieve': QuestionDetailSerializer,
        'create': QuestionCreateUpdateSerializer
    }
    permission_classes = {
        'create': (IsAdminUser,),
    }
    filterset_class = QuestionFilter

    def get_serializer_class(self):
        return self.serializer_mapping.get(self.action, QuestionDetailSerializer)

    def get_permissions(self):
        return [perm() for perm in self.permission_classes.get(self.action, [])]


class CompletedPollViewSet(ListModelMixin, viewsets.GenericViewSet):
    queryset = CompletedPoll.objects.all()
    serializer_mapping = {
        'list': CompletedPollListSerializer,
        'create': CompletedPollCreateSerializer
    }
    permission_classes = {
        'create': (IsAuthenticated,),
    }

    def get_serializer_class(self):
        return self.serializer_mapping.get(self.action, CompletedPollListSerializer)

    def get_permissions(self):
        return [perm() for perm in self.permission_classes.get(self.action, [])]

    def get_queryset(self):
        return self.queryset.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if CompletedPoll.objects.filter(poll=serializer.validated_data.get('poll'), user=request.user).exists():
            return Response({'error': 'Вы уже проходили данный опрос'}, status=status.HTTP_400_BAD_REQUEST)
        CompletedPoll.objects.create(**serializer.validated_data, user=request.user)
        return Response(status=status.HTTP_201_CREATED)


class PollUserViewSet(ListModelMixin, RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = PollUser.objects.all()
    serializer_mapping = {
        'list': PollUserListSerializer,
        'retrieve': PollUserDetailSerializer
    }

    def get_serializer_class(self):
        return self.serializer_mapping.get(self.action, PollUserListSerializer)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = PollUser.objects.get(uuid=kwargs.get('pk'))
        except PollUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
