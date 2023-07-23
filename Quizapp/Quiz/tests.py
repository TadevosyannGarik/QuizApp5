from .models import Question

question = Question.objects.first()  # Получите первый вопрос (вы можете выбрать нужный вопрос)
incorrect_answers = question.get_incorrect_answers()  # Получите неправильные ответы для данного вопроса

print(incorrect_answers)