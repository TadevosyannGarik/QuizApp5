import random
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Discipline, Topic, Question, IncorrectAnswer, Student, User, QuizResult
from .utils import save_discipline, save_topic, save_question
from .forms import RegistrationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            patronymic = form.cleaned_data['patronymic']
            date_of_birth = form.cleaned_data['date_of_birth']
            course = form.cleaned_data['course']

            existing_student = Student.objects.filter(
                first_name=first_name,
                last_name=last_name,
                patronymic=patronymic,
                date_of_birth=date_of_birth,
                course=course
            ).first()

            if existing_student:
                existing_user = User.objects.filter(student=existing_student).first()

                if existing_user:
                    return render(request, 'Quiz/student_registration.html', {'form': form, 'error': 'Пользователь с такими данными уже существует'})

                new_user = User.objects.create_user(username=email, email=email, password=password, student=existing_student)
                return redirect('login')
            else:
                return render(request, 'Quiz/student_registration.html', {'form': form, 'error': 'Пользователь с такими данными не существует'})

    else:
        form = RegistrationForm()
    return render(request, 'Quiz/student_registration.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['username']  # Вместо 'username' используем поле email для входа пользователя
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('after_login')  # Перенаправьте пользователя на страницу после успешного входа
    else:
        form = AuthenticationForm()
    return render(request, 'Quiz/login.html', {'form': form})


def success(request):
    return render(request, 'Quiz/success.html')


@login_required
def after_login(request):
    user_is_student = request.user.groups.filter(name='Student').exists()
    return render(request, 'Quiz/after_login.html', {'user_is_student': user_is_student})


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
    incorrect_answer = list(IncorrectAnswer.objects.filter(topic=topic).values_list('answer_text', flat=True))
    questions = topic.question_set.all()
    all_q = Question.objects.filter(topic=topic)
    list_question = []
    for i in all_q:
        tmp_list = []
        tmp_list.append(i.question_text)
        random.shuffle(incorrect_answer)
        answers = [i.correct_answer]
        count = 0
        while len(answers) < 4 and count < len(incorrect_answer):
            if incorrect_answer[count] != i.correct_answer:
                answers.append(incorrect_answer[count])
            count += 1
        random.shuffle(answers)
        tmp_list.append(answers)
        list_question.append(tmp_list)
    random.shuffle(list_question)

    if request.method == 'POST':
        score = 0
        for question in questions:
            selected_answer = request.POST.get(str(question.id))
            if selected_answer == question.correct_answer:
                score += 1

        user = request.user
        quiz_result = QuizResult.objects.create(
            user=user,
            topic=topic,
            score=score,
            date_completed=timezone.now()
        )
        quiz_result.save()

        return render(request, 'Quiz/result.html', {'score': score, 'total_questions': questions.count()})

    return render(request, 'Quiz/topic_detail.html',
                  {'topic': topic, 'questions': questions, 'list_question': list_question})


def result(request):
    return render(request, 'Quiz/result.html')