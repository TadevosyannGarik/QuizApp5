import random
from django.conf import settings
from django.utils import timezone, translation
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect

from . import models
from .models import Discipline, Topic, Question, IncorrectAnswer, Student, User, QuizResult, Preset, PresetQuestion, \
    Faculty, PresetQuestionResult
from .utils import save_discipline, save_topic, save_question
from .forms import RegistrationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg, Count, F, Sum


def student_statistics(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    quiz_results = QuizResult.objects.filter(user__student=student, date_completed__isnull=False)

    total_correct_answers = 0
    total_incorrect_answers = 0
    total_scores = 0
    total_grades = 0

    correct_answers_by_quiz = {}
    incorrect_answers_by_quiz = {}

    for result in quiz_results:
        preset_question_results = PresetQuestionResult.objects.filter(quiz_result=result)

        correct_answers = []
        incorrect_answers = []

        for pq_result in preset_question_results:
            if pq_result.student_answer == pq_result.question.correct_answer:
                correct_answers.append(pq_result.question.question_text)
            else:
                incorrect_answers.append(pq_result.question.question_text)

        correct_answers_by_quiz[result] = correct_answers
        incorrect_answers_by_quiz[result] = incorrect_answers

        total_scores += result.score
        total_correct_answers += len(correct_answers)
        total_incorrect_answers += len(incorrect_answers)
        total_grades += result.grade

    # Заменяем запятые на точки в значениях для графика
    average_correct_answers = round(total_correct_answers / len(quiz_results), 1) if len(quiz_results) > 0 else 0
    average_incorrect_answers = round(total_incorrect_answers / len(quiz_results), 1) if len(quiz_results) > 0 else 0
    average_grades = round(total_grades / len(quiz_results), 1) if len(quiz_results) > 0 else 0

    average_correct_answers = str(average_correct_answers).replace(',', '.')
    average_incorrect_answers = str(average_incorrect_answers).replace(',', '.')
    average_grades = str(average_grades).replace(',', '.')

    # Общий балл за пройденные тесты
    total_points = sum(result.score for result in quiz_results)

    # Средний балл
    average_score = round(total_points / len(quiz_results), 1) if len(quiz_results) > 0 else 0
    average_score = str(average_score).replace(',', '.')

    # Вычисляем общее количество тестов
    total_tests_taken = len(quiz_results)

    # Вычисляем среднее значение пройденных тестов
    average_tests_taken = round(total_tests_taken / len(quiz_results), 1) if len(quiz_results) > 0 else 0
    average_tests_taken = str(average_tests_taken).replace(',', '.')

    context = {
        'student': student,
        'correct_answers_by_quiz': correct_answers_by_quiz,
        'incorrect_answers_by_quiz': incorrect_answers_by_quiz,
        'total_correct_answers': total_correct_answers,
        'total_incorrect_answers': total_incorrect_answers,
        'average_correct_answers': average_correct_answers,
        'average_incorrect_answers': average_incorrect_answers,
        'average_grades': average_grades,
        'total_points': total_points,
        'average_score': average_score,
        'total_tests_taken': total_tests_taken,  # Передаем общее количество тестов
        'average_tests_taken': average_tests_taken,  # Передаем среднее значение пройденных тестов
    }

    return render(request, 'Quiz/student_statistics.html', context)


def is_teacher(user):
    return user.groups.filter(name="Teacher").exists()


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
            faculty = form.cleaned_data['faculty']

            existing_student = Student.objects.filter(
                first_name=first_name,
                last_name=last_name,
                patronymic=patronymic,
                date_of_birth=date_of_birth,
                course=course,
                faculty=faculty
            ).first()

            if existing_student:
                existing_user = User.objects.filter(student=existing_student).first()

                if existing_user:
                    return render(request, 'Quiz/student_registration.html', {'form': form, 'error': 'Пользователь с такими данными уже существует'})

                new_user = User.objects.create_user(username=email, email=email, password=password)
                new_user.student = existing_student
                new_user.save()

                student_group = Group.objects.get(name='Student')
                new_user.groups.add(student_group)

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
            email = form.cleaned_data['username']
            print(email)
            password = form.cleaned_data['password']
            print(password)
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('after_login')
        else:
            return render(request, 'Quiz/login.html', {'error': 'Не Верный Email или пароль'})
    else:
        form = AuthenticationForm()
    return render(request, 'Quiz/login.html', {'form': form})


def success(request):
    return render(request, 'Quiz/success.html')


def students_passed_test(request, preset_id):
    preset = Preset.objects.get(id=preset_id)
    student_results = QuizResult.objects.filter(preset=preset)

    passed_users = [
        {
            "user": result.user,
            "score": result.score,
            "grade": result.grade,
            "quiz_result_id": result.id,
        }
        for result in student_results
    ]

    return render(
        request,
        'Quiz/students_passed_test.html',
        {"preset": preset, "passed_users": passed_users}
    )


@login_required
def after_login(request):
    is_teacher = request.user.groups.filter(name='Teacher').exists()
    is_student = request.user.groups.filter(name='Student').exists()

    student_name = None

    if is_student:
        student = request.user.student
        if student:
            student_name = f"{student.first_name} {student.last_name}"

    user_allowed_disciplines = []
    all_disciplines = Discipline.objects.all()

    for discipline in all_disciplines:
        permission_codename = f'view_{discipline.name.replace(" ", "_").lower()}'
        user_has_permission = request.user.has_perm(f'Quiz.{permission_codename}')

        if user_has_permission:
            user_allowed_disciplines.append(discipline)

    user_allowed_topic_ids = []
    topics = Topic.objects.all()

    for topic in topics:
        permission_codename = f'view_topic_{topic.id}'
        if request.user.has_perm(f'Quiz.{permission_codename}'):
            user_allowed_topic_ids.append(topic.id)

    user_allowed_topics = topics.filter(id__in=user_allowed_topic_ids)

    user_results = QuizResult.objects.filter(user=request.user)

    if is_student:
        user_faculty = request.user.student.faculty
        completed_presets = QuizResult.objects.filter(user=request.user).values('preset')
        current_presets = Preset.objects.filter(faculty=user_faculty).exclude(id__in=completed_presets)
    else:
        current_presets = Preset.objects.all()
        completed_presets = []

    print("Current Presets:", current_presets)
    print("Completed Presets:", completed_presets)

    faculties = Faculty.objects.all()

    return render(request, 'Quiz/after_login.html',
                  {'is_teacher': is_teacher, 'is_student': is_student,
                   'student_name': student_name,
                   'disciplines': user_allowed_disciplines, 'topics': user_allowed_topics,
                   'user_results': user_results, 'faculties': faculties,
                   'current_presets': current_presets, 'completed_presets': completed_presets,     'student_id': student.id  # Убедитесь, что передаете student.id
})


def index(request):
    return render(request, 'Quiz/index.html')


@login_required
@user_passes_test(is_teacher)
def add_discipline(request):
    print("User:", request.user)
    print("Преподаватель ?", is_teacher(request.user))

    if request.method == 'POST':
        discipline_name = request.POST.get('name')
        if discipline_name:
            discipline = save_discipline(discipline_name)

            permission_codename = f'view_{discipline.name.replace(" ", "_").lower()}'
            print(permission_codename)
            permission_name = f'Can view {discipline.name}'
            print(permission_name)
            content_type = ContentType.objects.get(app_label='Quiz', model='discipline')
            print(content_type)
            permission, created = Permission.objects.get_or_create(
                codename=permission_codename,
                name=permission_name,
                content_type=content_type,
            )

            request.user.user_permissions.add(permission)
            print(f"Разрешение добавлено пользователю: {request.user.email}, Разрешение: {permission_codename}")

            return redirect('discipline_list')
    else:
        messages.error(request, "У вас не достаточно прав для добавления дисциплины")
    return render(request, 'Quiz/add_discipline.html')


@login_required
@user_passes_test(is_teacher)
def add_topic(request):
    disciplines = Discipline.objects.all()

    if request.method == 'POST':
        discipline_id = request.POST.get('discipline')
        topic_name = request.POST.get('name')

        if discipline_id and topic_name:
            discipline = Discipline.objects.get(id=discipline_id)
            save_topic(discipline_id, topic_name, user=request.user)

            permission_codename = f'view_{topic_name.replace(" ", "_").lower()}'
            permission_name = f'Can view {topic_name}'
            content_type = ContentType.objects.get(app_label='Quiz', model='topic')
            permission, created = Permission.objects.get_or_create(
                codename=permission_codename,
                name=permission_name,
                content_type=content_type,
            )

            request.user.user_permissions.add(permission)
            print(f"Разрешение добавлено пользователю: {request.user.email}, Разрешение {permission_codename}")

            return redirect('topic_list')

    return render(request, 'Quiz/add_topic.html', {'disciplines': disciplines})


def topic_list(request):
    topics = Topic.objects.all()
    return render(request, 'Quiz/topic_list.html', {'topics': topics})


@login_required
def discipline_list(request):
    user_allowed_disciplines = []

    all_disciplines = Discipline.objects.all()

    for discipline in all_disciplines:
        permission_codename = f'view_{discipline.name.replace(" ", "_").lower()}'
        user_has_permission = request.user.has_perm(f'QuizApp.{permission_codename}')
        print(f"Дисциплина: {discipline.name}, User: {request.user.email}, Имеет разрешение: {user_has_permission}")

        if user_has_permission:
            user_allowed_disciplines.append(discipline)

    return render(request, 'Quiz/discipline_list.html', {'disciplines': user_allowed_disciplines})

@login_required
@user_passes_test(is_teacher)
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
            question_points = int(request.POST.get(f'question_points_{i}'))
            answer_mode = request.POST.get(f'answer_mode_{i}')
            image = request.FILES.get(f'image_{i}')

            if topic_id and question_text and correct_answer and answer_mode:
                save_question(topic_id, question_text, correct_answer, question_points, answer_mode, image)

        return redirect('index')

    return render(request, 'Quiz/add_question.html', {'topics': topics})




def test_list(request):
    tests = Topic.objects.all()
    return render(request, 'Quiz/test_list.html', {'tests': tests})


def topic_detail(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    all_q = Question.objects.filter(topic=topic)
    list_question = []

    total_points = 0

    for i in all_q:
        tmp_list = []
        tmp_list.append(i.question_text)
        answers = [(i.correct_answer, i.points)]
        count = 0
        while len(answers) < 4 and count < len(all_q) - 1:
            if all_q[count].correct_answer != i.correct_answer:
                answers.append((all_q[count].correct_answer, 0))
            count += 1
        random.shuffle(answers)
        tmp_list.append(answers)
        list_question.append(tmp_list)
        total_points += i.points

    random.shuffle(list_question)

    if request.method == 'POST':
        score = 0

        for question_data in list_question:
            selected_answer = request.POST.get("question_" + str(question_data[0]))
            for ans_id, points in question_data[1]:
                if ans_id == selected_answer:
                    score += points
                    break

        user = request.user
        quiz_result = QuizResult.objects.create(
            user=user,
            topic=topic,
            score=score,
            total_points=total_points,
            date_completed=timezone.now()
        )
        quiz_result.save()

        return render(request, 'Quiz/result.html', {'score': score, 'total_questions': all_q.count()})

    return render(request, 'Quiz/topic_detail.html',  {'topic': topic, 'questions': all_q, 'list_question': list_question})


def generate_test(request):
    faculties = Faculty.objects.all()
    user_allowed_topic_ids = []
    topics = Topic.objects.all()

    for topic in topics:
        permission_codename = f'view_topic_{topic.id}'
        if request.user.has_perm(f'QuizApp.{permission_codename}'):
            user_allowed_topic_ids.append(topic.id)

    user_allowed_topics = topics.filter(id__in=user_allowed_topic_ids)

    if request.method == 'POST':
        selected_faculty_id = request.POST.get('faculty')
        selected_faculty = Faculty.objects.get(pk=selected_faculty_id)
        name = request.POST.get('preset_name')
        description = request.POST.get('preset_description')
        selected_topic_id = request.POST.get('topic')
        num_questions = int(request.POST.get('num_questions'))

        selected_topic = Topic.objects.get(pk=selected_topic_id)

        preset = Preset(
            name=name,
            description=description,
            faculty=selected_faculty,
            topic=selected_topic,
        )
        preset.save()

        questions_from_topic = selected_topic.question_set.all()
        num_questions = min(num_questions, questions_from_topic.count())
        selected_questions = questions_from_topic.order_by('?')[:num_questions]
        all_incorrect_answers = list(IncorrectAnswer.objects.filter(topic=selected_topic))

        for question in selected_questions:
            answer_mode = question.answer_mode
            preset_question = PresetQuestion(preset=preset, question=question)
            preset_question.save()

            if answer_mode == 'choose':
                num_incorrect_answers_to_select = min(3, len(all_incorrect_answers))
                selected_incorrect_answers = random.sample(all_incorrect_answers, num_incorrect_answers_to_select)
                for incorrect_answer in selected_incorrect_answers:
                    preset_question.incorrect_answers.add(incorrect_answer)
                preset_question.correct_answer = question.correct_answer
            else:
                preset_question.correct_answer = question.correct_answer

            print(f"Вопрос: {question.question_text}")
            print(f"Верный ответ: {preset_question.correct_answer}")
            print("Неверные ответы:")
            for incorrect_answer in preset_question.incorrect_answers.all():
                print(incorrect_answer.answer_text)
            print()

        return redirect('preset_list')

    context = {'faculties': faculties, 'user_allowed_topics': user_allowed_topics, 'topics': user_allowed_topics}
    return render(request, 'Quiz/generate_test.html', context)


def preset_list(request):
    presets = Preset.objects.all()
    return render(request, 'Quiz/preset_list.html', {'presets': presets})


def faculty_preset_list(request):
    user = request.user
    if hasattr(user, 'student'):
        user_faculty = user.student.faculty
        presets = Preset.objects.filter(faculty=user_faculty)
    else:
        presets = Preset.objects.none()

    return render(request, "Quiz/faculty_preset_list.html", {'presets': presets})


def preset_detail(request, preset_id):
    preset = get_object_or_404(Preset, pk=preset_id)
    preset_questions = PresetQuestion.objects.filter(preset=preset)
    total_points = sum(question.question.points for question in preset_questions)
    question_dict = {}

    for preset_question in preset_questions:
        question = preset_question.question
        tmp_list = [question.question_text]

        answer_mode = question.answer_mode
        if answer_mode == 'choose':
            incorrect_answers = list(preset_question.incorrect_answers.all())
            answers = [(question.correct_answer, question.points, question.id)]
            while len(answers) < 4 and len(incorrect_answers) > 0:
                incorrect_answer = incorrect_answers.pop()
                answers.append((incorrect_answer.answer_text, 0, incorrect_answer.id))
            random.shuffle(answers)
        else:
            answers = []

        question_dict[question.id] = tmp_list + [answers, answer_mode, question.image]

    if request.method == 'POST':
        quiz_result = QuizResult(user=request.user, preset=preset, total_points=total_points,
                                 date_completed=timezone.now())
        quiz_result.save()
        score = 0
        for question_id, question_data in question_dict.items():
            selected_answer = request.POST.get("question_" + str(question_id))
            question = Question.objects.get(id=question_id)

            if question_data[2] == 'choose':
                selected_answer_text = None
                for ans_id, points, _ in question_data[1]:
                    if ans_id == selected_answer:
                        selected_answer_text = ans_id
                        score += points
                        break

                preset_question_result = PresetQuestionResult(
                    quiz_result=quiz_result,
                    student=request.user.student,
                    question=question,
                    student_answer=selected_answer_text,
                    question_score=score
                )
                preset_question_result.save()
            elif question_data[2] == 'input':
                user_input = request.POST.get("question_" + str(question_id))
                correct_answer = question.correct_answer
                if user_input.strip().lower() == correct_answer.strip().lower():
                    score += question.points

                preset_question_result = PresetQuestionResult(
                    quiz_result=quiz_result,
                    student=request.user.student,
                    question=question,
                    student_answer=user_input,
                    question_score=question.points if user_input.strip().lower() == correct_answer.strip().lower() else 0
                )
                preset_question_result.save()

        quiz_result.score = score
        quiz_result.save()

        return redirect('result', quiz_result_id=quiz_result.id)

    context = {'preset': preset, 'preset_questions': preset_questions, 'total_points': total_points, 'question_dict': question_dict}
    return render(request, 'Quiz/preset_detail.html', context)


def result(request, quiz_result_id):
    quiz_result = QuizResult.objects.get(id=quiz_result_id)
    user = quiz_result.user.student
    preset = quiz_result.preset
    questions = Question.objects.filter(topic=preset.topic)
    percentage_score = (quiz_result.score / quiz_result.total_points) * 100

    question_results = PresetQuestionResult.objects.filter(quiz_result=quiz_result)

    for result in question_results:
        question_text = result.question.question_text
        if len(question_text.split()) > 15:
            result.question.question_text_short = ' '.join(question_text.split()[:15]) + ''
        else:
            result.question.question_text_short = question_text

    context = {
        'quiz_result': quiz_result,
        'user': user,
        'preset': preset,
        'questions': questions,
        'question_results': question_results,
        'percentage_score': percentage_score,
    }

    return render(request, 'Quiz/result.html', context)


def edit_preset(request, preset_id):
    preset = get_object_or_404(Preset, id=preset_id)

    if request.method == 'POST':
        preset_name = request.POST.get('name', '')
        preset.name = preset_name
        preset.save()

        for preset_question in preset.presetquestion_set.all():
            question_id = request.POST.get(f"question_select_{preset_question.id}")
            correct_answer = request.POST.get(f"correct_answer_{preset_question.id}", '')

            question = Question.objects.get(id=question_id)
            preset_question.question = question
            preset_question.correct_answer = correct_answer

            selected_incorrect_answer_ids = request.POST.getlist(f"incorrect_answer_select_{preset_question.id}")
            selected_incorrect_answers = IncorrectAnswer.objects.filter(id__in=selected_incorrect_answer_ids)

            preset_question.incorrect_answers.clear()

            for incorrect_answer in selected_incorrect_answers:
                preset_question.incorrect_answers.add(incorrect_answer)

            preset_question.save()

        return redirect('preset_list')

    all_questions = Question.objects.all()
    all_incorrect_answers = IncorrectAnswer.objects.all()

    return render(request, 'Quiz/edit_preset.html', {
        'preset': preset,
        'all_questions': all_questions,
        'all_incorrect_answers': all_incorrect_answers,
    })
