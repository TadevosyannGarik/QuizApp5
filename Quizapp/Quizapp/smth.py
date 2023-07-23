import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Quiz.settings')

import django
django.setup()

from Quizapp.Quiz.models import Question

question = Question.objects.first()
incorrect_answers = question.get_incorrect_answers()

print(incorrect_answers)
