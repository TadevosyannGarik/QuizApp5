from django import forms
from django.forms import inlineformset_factory

from .models import Discipline, Topic, Question, IncorrectAnswer


class DisciplineForm(forms.ModelForm):
    class Meta:
        model = Discipline
        fields = ['name']


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['discipline', 'name']


TopicIncorrectAnswerFormSet = inlineformset_factory(
    Topic,
    IncorrectAnswer,
    fields=('answer_text',),
    extra=1,
    can_delete=True
)


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['topic', 'question_text']



