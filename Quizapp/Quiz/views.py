from django.shortcuts import render, get_object_or_404, redirect
from .models import Discipline, Topic, Question, IncorrectAnswer
from .utils import save_discipline, save_topic, save_incorrect_answer, save_question


def index(request):
    return render(request, 'Quiz/index.html')


def add_discipline(request):
    if request.method == 'POST':
        discipline_name = request.POST.get('name')
        if discipline_name:
            save_discipline(discipline_name)
            return redirect('discipline_list')
    return render(request, 'Quiz/add_discipline.html')


def add_topic(request):
    disciplines = Discipline.objects.all()

    if request.method == 'POST':
        discipline_id = request.POST.get('discipline')
        topic_name = request.POST.get('name')

        if discipline_id and topic_name:
            save_topic(discipline_id, topic_name)
            return redirect('topic_list')

    return render(request, 'Quiz/add_topic.html', {'disciplines': disciplines})


def topic_list(request):
    topics = Topic.objects.all()
    return render(request, 'Quiz/topic_list.html', {'topics': topics})


def discipline_list(request):
    disciplines = Discipline.objects.all()
    return render(request, 'Quiz/discipline_list.html', {'disciplines': disciplines})


def add_incorrect_answer(request):
    if request.method == 'POST':
        topic_id = request.POST.get('topic_id')
        answer_text = request.POST.get('answer_text')

        if topic_id and answer_text:
            topic = Topic.objects.get(id=topic_id)
            incorrect_answer = IncorrectAnswer(topic=topic, answer_text=answer_text)
            incorrect_answer.save()
            return redirect('topic_detail', topic_id=topic_id)

    topics = Topic.objects.all()
    return render(request, 'Quiz/add_incorrect_answer.html', {'topics': topics})


def add_question(request):
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_id = request.POST.get('topic')
        question_count = int(request.POST.get('question_count'))

        for i in range(1, question_count + 1):
            question_text = request.POST.get(f'question_text_{i}')
            correct_answer = request.POST.get(f'correct_answer_{i}')

            if topic_id and question_text and correct_answer:
                save_question(topic_id, question_text, correct_answer)

        return redirect('index  ')

    return render(request, 'Quiz/add_question.html', {'topics': topics})


def test_list(request):
    tests = Topic.objects.all()
    return render(request, 'Quiz/test_list.html', {'tests': tests})


def topic_detail(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    questions = topic.question_set.all()

    if request.method == 'POST':
        score = 0

        for question in questions:
            selected_answer = request.POST.get(str(question.id))  # Получаем выбранный ответ из POST-запроса

            if selected_answer == question.correct_answer:
                score += 1

        return render(request, 'Quiz/result.html', {'score': score, 'total_questions': questions.count()})

    return render(request, 'Quiz/topic_detail.html', {'topic': topic, 'questions': questions})

