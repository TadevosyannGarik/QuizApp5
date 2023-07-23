from django.contrib import admin
from .models import Discipline, Topic, Question, IncorrectAnswer


admin.site.register(Discipline)
admin.site.register(Topic)
admin.site.register(Question)
admin.site.register(IncorrectAnswer)
