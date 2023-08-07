from django import forms
from django.forms import inlineformset_factory
from .models import Discipline, Topic, Question, IncorrectAnswer, User, Faculty
from .models import User, Student


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


class AdminLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    patronymic = forms.CharField(max_length=100)
    date_of_birth = forms.DateField()
    course = forms.CharField(max_length=100)
    faculty = forms.ModelChoiceField(queryset=Faculty.objects.all())
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email']
        user_exists = User.objects.filter(email=email).exists()
        if user_exists:
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email

    def save(self):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        patronymic = self.cleaned_data['patronymic']
        date_of_birth = self.cleaned_data['date_of_birth']
        course = self.cleaned_data['course']

        student = Student.objects.create(
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            date_of_birth=date_of_birth,
            course=course
        )

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            student=student
        )

        return user