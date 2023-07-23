from django.db import models


class Discipline(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Topic(models.Model):
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class IncorrectAnswer(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=100)

    def __str__(self):
        return self.answer_text


class Question(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    question_text = models.TextField()
    correct_answer = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.question_text

    def get_incorrect_answers(self):
        incorrect_answers = IncorrectAnswer.objects.filter(topic=self.topic).order_by('?')[:3]
        return [answer.answer_text for answer in incorrect_answers]



