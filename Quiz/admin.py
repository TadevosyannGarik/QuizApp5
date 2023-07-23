from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Discipline, Topic, Question, IncorrectAnswer, Student, User, QuizResult

admin.site.register(QuizResult)


class DisciplineAdmin(admin.ModelAdmin):
    list_display = ['name']


class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'discipline']
    list_filter = ['discipline']


class IncorrectAnswerAdmin(admin.ModelAdmin):
    list_display = ['answer_text', 'topic']
    list_filter = ['topic']


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'topic', 'correct_answer']
    list_filter = ['topic']
    search_fields = ['question_text']


class StudentAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'patronymic', 'date_of_birth', 'course']


class UserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'student']
    search_fields = ['username', 'email', 'first_name', 'last_name']


admin.site.register(Discipline, DisciplineAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(IncorrectAnswer, IncorrectAnswerAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Student, StudentAdmin)

admin.site.register(User, UserAdmin)
