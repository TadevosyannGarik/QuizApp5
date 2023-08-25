import random
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from .models import Discipline, Topic, Question, IncorrectAnswer, Student, User, QuizResult, Preset, PresetQuestion, \
    Faculty
from .utils import save_discipline, save_topic, save_question
from .forms import RegistrationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


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
            return render(request, 'Quiz/login.html',{'error': 'Не Верный Email или пароль'})
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
        user_has_permission = request.user.has_perm(f'QuizApp.{permission_codename}')

        if user_has_permission:
            user_allowed_disciplines.append(discipline)

    user_allowed_topic_ids = []
    topics = Topic.objects.all()

    for topic in topics:
        permission_codename = f'view_topic_{topic.id}'
        if request.user.has_perm(f'QuizApp.{permission_codename}'):
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
                   'current_presets': current_presets, 'completed_presets': completed_presets})


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
            content_type = ContentType.objects.get(app_label='QuizApp', model='discipline')
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
            content_type = ContentType.objects.get(app_label='QuizApp', model='topic')
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


@login_required
@user_passes_test(is_teacher)
def add_question(request):
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_id = request.POST.get('topic')
        question_count = int(request.POST.get('question_count'))

        for i in range(1, question_count + 1):
            question_text = request.POST.get(f'question_text_{i}')
            correct_answer = request.POST.get(f'correct_answer_{i}')
            question_points = int(request.POST.get(f'question_points_{i}'))

            if topic_id and question_text and correct_answer:
                save_question(topic_id, question_text, correct_answer, question_points)

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


def result(request):
    return render(request, 'Quiz/result.html')


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
        answer_mode = request.POST.get('answer_mode')

        selected_topic = Topic.objects.get(pk=selected_topic_id)

        preset = Preset(name=name, description=description, faculty=selected_faculty, topic=selected_topic)
        preset.save()

        questions_from_topic = selected_topic.question_set.all()
        num_questions = min(num_questions, questions_from_topic.count())
        selected_questions = questions_from_topic.order_by('?')[:num_questions]
        all_incorrect_answers = list(IncorrectAnswer.objects.filter(topic=selected_topic))

        selected_incorrect_answers_dict = {}

        for question in selected_questions:
            preset_question = PresetQuestion(preset=preset, question=question)
            preset_question.save()

            if answer_mode == 'choose':
                num_incorrect_answers_to_select = min(3, len(all_incorrect_answers))
                selected_incorrect_answers = random.sample(all_incorrect_answers, num_incorrect_answers_to_select)
                selected_incorrect_answers_dict[question.id] = selected_incorrect_answers
                for incorrect_answer in selected_incorrect_answers:
                    preset_question.incorrect_answers.add(incorrect_answer)
                    print(selected_incorrect_answers_dict)

        return redirect('preset_list')

    context = {'faculties': faculties, 'user_allowed_topics': user_allowed_topics, 'topics': user_allowed_topics,}
    return render(request, 'Quiz/generate_test.html', context, )



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

        incorrect_answers = list(preset_question.incorrect_answers.all())
        answers = [(question.correct_answer, question.points, question.id)]
        while len(answers) < 4 and len(incorrect_answers) > 0:
            incorrect_answer = incorrect_answers.pop()
            answers.append((incorrect_answer.answer_text, 0, incorrect_answer.id))
        random.shuffle(answers)
        question_dict[question.id] = tmp_list + [answers]
    question_ids = list(question_dict.keys())
    random.shuffle(question_ids)
    question_dict = {qid: question_dict[qid] for qid in question_ids}
    if request.method == 'POST':
        score = 0
        for question_id, question_data in question_dict.items():
            selected_answer = request.POST.get("question_" + str(question_id))
            for ans_id, points, _ in question_data[1]:
                if ans_id == selected_answer:
                    score += points
                    break
        user = request.user
        quiz_result = QuizResult.objects.create(
            user=user,
            preset=preset,
            score=score,
            total_points=total_points,
            date_completed=timezone.now()
        )
        quiz_result.save()
        return render(request, 'Quiz/result.html', {'score': score, 'total_questions': len(preset_questions)})
    return render(request, 'Quiz/preset_detail.html', {
        'preset': preset,
        'preset_questions': preset_questions,
        'total_points': total_points,
        'question_dict': question_dict,
    })


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