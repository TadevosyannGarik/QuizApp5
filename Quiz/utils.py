from .models import Discipline, Topic, IncorrectAnswer, Question
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission


def save_discipline(discipline_name):
    discipline = Discipline(name=discipline_name)
    discipline.save()
    return discipline


def save_topic(discipline_id, name, user=None):
    discipline = Discipline.objects.get(id=discipline_id)
    topic = Topic(discipline=discipline, name=name)
    topic.save()
    topic.save()
    permission_codename = f'view_topic_{topic.id}'
    permission_name = f'Can view topic: {topic.name}'
    content_type = ContentType.objects.get_for_model(topic)
    permission, _ = Permission.objects.get_or_create(
        codename=permission_codename,
        name=permission_name,
        content_type=content_type,
    )

    if user:
        user.user_permissions.add(permission)

    return topic


def save_incorrect_answer(topic_id, answer_text):
    topic = Topic.objects.get(id=topic_id)
    incorrect_answer = IncorrectAnswer(topic=topic, answer_text=answer_text)
    incorrect_answer.save()
    return incorrect_answer


def save_question(topic_id, question_text, correct_answer, question_points):
    topic = Topic.objects.get(id=topic_id)
    question = Question(topic=topic, question_text=question_text, correct_answer=correct_answer, points=question_points)
    question.save()
    return question


