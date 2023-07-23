from django.shortcuts import redirect, render
from .models import Discipline, Topic, IncorrectAnswer, Question


def save_discipline(discipline_name):
    discipline = Discipline(name=discipline_name)
    discipline.save()
    return discipline


def save_topic(discipline_id, name):
    discipline = Discipline.objects.get(id=discipline_id)
    topic = Topic(discipline=discipline, name=name)
    topic.save()
    return topic


def save_incorrect_answer(topic_id, answer_text):
    topic = Topic.objects.get(id=topic_id)
    incorrect_answer = IncorrectAnswer(topic=topic, answer_text=answer_text)
    incorrect_answer.save()
    return incorrect_answer


def save_question(topic_id, question_text, correct_answer):
    topic = Topic.objects.get(id=topic_id)
    question = Question(topic=topic, question_text=question_text, correct_answer=correct_answer)
    question.save()
    return question