from django.contrib import admin

# Register your models here.
from polls.models import Question, Poll, AnswerChoice


class AnswerChoiceInline(admin.TabularInline):
    model = AnswerChoice
    extra = 4


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    model = Question
    search_fields = ('poll__name', 'text')
    inlines = (AnswerChoiceInline, )


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 4


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    model = Poll
    search_fields = ('name', )
    readonly_fields = ('start_date', )
    inlines = (QuestionInline, )
