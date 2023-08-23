from django.contrib.auth.models import AbstractUser
from django.db import models


class Discipline(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Topic(models.Model):
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Question(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    question_text = models.TextField()
    correct_answer = models.CharField(max_length=100, default='')
    points = models.IntegerField(default=0)

    def __str__(self):
        return self.question_text


class IncorrectAnswer(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=100)

    def __str__(self):
        return self.answer_text


class Faculty(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Preset(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class PresetQuestion(models.Model):
    preset = models.ForeignKey(Preset, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    incorrect_answers = models.ManyToManyField(IncorrectAnswer, blank=True)
    correct_answer = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Preset: {self.preset.name} - Question: {self.question.question_text}"


class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    patronymic = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    course = models.CharField(max_length=100, null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class User(AbstractUser):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, null=True, blank=True, unique=True)

    def __str__(self):
        return self.email


class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    preset = models.ForeignKey(Preset, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)
    grade = models.IntegerField(default=0)

    date_completed = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} - {self.preset.name} - Score: {self.score}"

    def calculate_grade(self):
        if self.score >= 80:
            return 5
        elif self.score >= 60:
            return 4
        elif self.score >= 40:
            return 3
        else:
            return 2

    def save(self, *args, **kwargs):
        self.grade = self.calculate_grade()
        super().save(*args, **kwargs)

