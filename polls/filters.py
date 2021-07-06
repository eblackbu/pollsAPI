from datetime import date

from django_filters import rest_framework as filters

from polls.models import Poll, Question


class PollFilter(filters.FilterSet):
    actual = filters.BooleanFilter(method='is_actual')

    class Meta:
        model = Poll
        fields = ('actual', )

    def is_actual(self, queryset, name, value):
        return queryset.filter(end_date__gte=date.today()) if value else queryset


class QuestionFilter(filters.FilterSet):
    poll_name = filters.CharFilter(label='Название опроса', method='filter_by_poll_name')

    def filter_by_poll_name(self, queryset, name, value):
        return queryset.filter(poll__name__icontains=value) if value else queryset

    class Meta:
        model = Question
        fields = ('poll', 'poll_name')
