from django.contrib.auth.models import AbstractUser
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
    points = models.IntegerField(default=0)

    def get_incorrect_answers(self):
        incorrect_answers = IncorrectAnswer.objects.filter(topic=self.topic).exclude(answer_text=self.correct_answer).order_by('?')[:3]
        return [answer.answer_text for answer in incorrect_answers]


class Preset(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class PresetQuestion(models.Model):
    preset = models.ForeignKey(Preset, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    incorrect_answers = models.ManyToManyField(IncorrectAnswer)

    def __str__(self):
        return f"Preset: {self.preset.name} - Question: {self.question.question_text}"


class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    patronymic = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    course = models.CharField(max_length=100, null=True)


class User(AbstractUser):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, null=True, blank=True, unique=True)

    def __str__(self):
        return self.email


class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)
    date_completed = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} - {self.topic.name} - Score: {self.score}"