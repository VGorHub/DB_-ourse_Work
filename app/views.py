# app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone

from .models import AppUser, Employee, Question, Test, Answer, TestResult, TestDeletionRequest
from .forms import AppUserForm, EmployeeForm, UserSelectionForm, EmployeeAdminForm, AppUserAdminForm, \
    TestDeletionRequestForm, AddTestForm, AnswerForm, QuestionForm

# DRF импорты
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, EmployeeSerializer

def get_current_user(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return None, None
    try:
        app_user = AppUser.objects.get(id=user_id)
        role_name = app_user.role
        return app_user, role_name
    except AppUser.DoesNotExist:
        return None, None

def login_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        app_user, role_name = get_current_user(request)
        if not app_user:
            return redirect('set_user')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def index(request):
    app_user, role_name = get_current_user(request)
    if not app_user:
        return redirect('set_user')
    return render(request, 'index.html', {'role': role_name, 'user_id': app_user.id, 'app_user': app_user})

def set_user(request):
    if request.method == 'POST':
        form = UserSelectionForm(request.POST)
        if form.is_valid():
            app_user = form.cleaned_data['user']
            request.session['user_id'] = app_user.id
            messages.success(request, f'Вы вошли как {app_user.full_name}')
            return redirect('index')
    else:
        form = UserSelectionForm()
    return render(request, 'set_user.html', {'form': form})

@login_required
def user_list(request):
    app_user, role_name = get_current_user(request)
    if role_name != 'admin':
        return HttpResponse('У вас нет доступа к этой странице', status=403)

    search_query = request.GET.get('search', '').strip()
    sort_by = request.GET.get('sort', 'id')
    order = request.GET.get('order', 'asc')

    user_list = AppUser.objects.filter(
        Q(full_name__icontains=search_query) | Q(email__icontains=search_query)
    )

    if order == 'desc':
        sort_by = '-' + sort_by
    user_list = user_list.order_by(sort_by)

    paginator = Paginator(user_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'user_list.html', {
        'page_obj': page_obj,
        'role': role_name
    })

@login_required
def user_detail(request, user_id):
    app_user, role_name = get_current_user(request)

    target_user = get_object_or_404(AppUser, id=user_id)

    if role_name != 'admin' and app_user.id != target_user.id:
        return HttpResponse('У вас нет доступа к этой странице', status=403)

    if request.method == 'POST':
        if role_name == 'admin':
            form = AppUserAdminForm(request.POST, instance=target_user)
        else:
            form = AppUserForm(request.POST, instance=target_user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные пользователя обновлены')
            return redirect('user_detail', user_id=user_id)
    else:
        if role_name == 'admin':
            form = AppUserAdminForm(instance=target_user)
        else:
            form = AppUserForm(instance=target_user)

    return render(request, 'user_detail.html', {
        'form': form,
        'app_user': target_user,
        'role': role_name
    })

@login_required
def employee_list(request):
    app_user, role_name = get_current_user(request)
    if role_name not in ['admin', 'employee']:
        return HttpResponse('У вас нет доступа к этой странице', status=403)

    search_query = request.GET.get('search', '').strip()
    sort_by = request.GET.get('sort', 'id')
    order = request.GET.get('order', 'asc')

    ALLOWED_SORT_FIELDS = ['id', 'user__full_name', 'user__email', 'position', 'salary']

    if sort_by not in ALLOWED_SORT_FIELDS:
        sort_by = 'id'

    if order == 'desc':
        sort_by = '-' + sort_by

    if role_name == 'admin':
        employee_list = Employee.objects.filter(
            Q(user__full_name__icontains=search_query) | Q(user__email__icontains=search_query)
        ).select_related('user').order_by(sort_by)
    elif role_name == 'employee':
        employee_list = Employee.objects.filter(user=app_user).select_related('user').order_by(sort_by)
    else:
        employee_list = Employee.objects.none()

    paginator = Paginator(employee_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'employee_list.html', {
        'page_obj': page_obj,
        'role': role_name
    })

@login_required
def employee_detail(request, employee_id):
    app_user, role_name = get_current_user(request)

    employee = get_object_or_404(Employee, id=employee_id)

    if role_name == 'employee':
        if employee.user.id != app_user.id:
            return HttpResponse('У вас нет доступа к этой странице', status=403)
        if request.method == 'POST':
            form = EmployeeForm(request.POST, request.FILES, instance=employee)
            if form.is_valid():
                form.save()
                messages.success(request, 'Данные сотрудника обновлены')
                return redirect('employee_detail', employee_id=employee_id)
        else:
            form = EmployeeForm(instance=employee)
    elif role_name == 'admin':
        if request.method == 'POST':
            form = EmployeeAdminForm(request.POST, request.FILES, instance=employee)
            if form.is_valid():
                form.save()
                messages.success(request, 'Данные сотрудника обновлены')
                return redirect('employee_detail', employee_id=employee_id)
        else:
            form = EmployeeAdminForm(instance=employee)
    else:
        return HttpResponse('У вас нет доступа к этой странице', status=403)

    return render(request, 'employee_detail.html', {
        'form': form,
        'employee': employee,
        'role': role_name
    })

@login_required
def add_user(request):
    app_user, role_name = get_current_user(request)
    if role_name != 'admin':
        return HttpResponse('У вас нет доступа к этой странице', status=403)

    if request.method == 'POST':
        form = AppUserForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.role = 'user'
            new_user.save()
            messages.success(request, 'Новый пользователь добавлен')
            return redirect('user_list')
    else:
        form = AppUserForm()

    return render(request, 'add_user.html', {'form': form, 'role': role_name})

@login_required
def add_employee(request):
    app_user, role_name = get_current_user(request)
    if role_name != 'admin':
        return HttpResponse('У вас нет доступа к этой странице', status=403)

    if request.method == 'POST':
        form = EmployeeAdminForm(request.POST, request.FILES)
        if form.is_valid():
            # Создаём AppUser сначала
            new_user = AppUser(
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                age=form.cleaned_data['age'],
                role=form.cleaned_data['role']
            )
            new_user.save()
            new_employee = Employee(
                user=new_user,
                years_of_experience=form.cleaned_data['years_of_experience'],
                position=form.cleaned_data['position'],
                salary=form.cleaned_data['salary'],
                photo=form.cleaned_data['photo']
            )
            new_employee.save()
            messages.success(request, 'Новый сотрудник добавлен')
            return redirect('employee_list')
    else:
        form = EmployeeAdminForm()

    return render(request, 'add_employee.html', {'form': form, 'role': role_name})

@login_required
def delete_user(request, user_id):
    app_user, role_name = get_current_user(request)
    if role_name != 'admin':
        return HttpResponse('У вас нет доступа к этой странице', status=403)

    target_user = get_object_or_404(AppUser, id=user_id)
    target_user.delete()
    messages.success(request, 'Пользователь удалён')
    return redirect('user_list')

@login_required
def delete_employee(request, employee_id):
    # Удаление сотрудника сейчас не обязательно изменять, но оставим как есть
    app_user, role_name = get_current_user(request)
    if role_name != 'admin':
        return HttpResponse('У вас нет доступа к этой странице', status=403)

    employee = get_object_or_404(Employee, id=employee_id)
    employee.delete()
    messages.success(request, 'Сотрудник удалён')
    return redirect('employee_list')


@login_required
def fire_employee(request, employee_id):
    app_user, role_name = get_current_user(request)
    if role_name != 'admin':
        return HttpResponse('У вас нет доступа', status=403)

    employee = get_object_or_404(Employee, id=employee_id)
    if not employee.is_fired:
        employee.is_fired = True
        employee.save()
        messages.success(request, 'Сотрудник уволен. Теперь его можно полностью удалить из БД.')
    else:
        messages.warning(request, 'Сотрудник уже уволен.')
    return redirect('employee_list')

@login_required
def delete_fired_employee(request, employee_id):
    app_user, role_name = get_current_user(request)
    if role_name != 'admin':
        return HttpResponse('У вас нет доступа', status=403)

    employee = get_object_or_404(Employee, id=employee_id)
    if employee.is_fired:
        # Сначала удаляем связанного пользователя
        user = employee.user
        employee.delete()
        user.delete()
        messages.success(request, 'Сотрудник и его пользовательские данные полностью удалены из БД.')
    else:
        messages.warning(request, 'Невозможно удалить: сотрудник не помечен как уволенный.')
    return redirect('employee_list')


@login_required
def test_list(request):
    app_user, role_name = get_current_user(request)

    search_query = request.GET.get('search', '').strip()
    sort_by = request.GET.get('sort', 'title')
    order = request.GET.get('order', 'asc')

    test_list = Test.objects.filter(
        Q(title__icontains=search_query) | Q(description__icontains=search_query)
    )

    if order == 'desc':
        sort_by = '-' + sort_by
    test_list = test_list.order_by(sort_by)

    paginator = Paginator(test_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'test_list.html', {
        'page_obj': page_obj,
        'role': role_name
    })

@login_required
def start_test(request, test_id):
    app_user, role_name = get_current_user(request)

    test = get_object_or_404(Test, id=test_id)
    questions = Question.objects.filter(test=test).prefetch_related('answer_set')

    if request.method == 'POST':
        selected_answers = request.POST.getlist('answers')
        correct_answers = Answer.objects.filter(question__test=test, is_correct=True).values_list('id', flat=True)
        score = sum(1 for ans_id in selected_answers if int(ans_id) in correct_answers)
        status = 'passed' if score >= test.passing_score else 'failed'
        employee = Employee.objects.filter(user=app_user).first()
        attempt_number = TestResult.objects.filter(user=app_user, test=test).count() + 1
        test_result = TestResult.objects.create(
            user=app_user,
            test=test,
            employee=employee,
            test_date=timezone.now(),
            score_achieved=score,
            status=status,
            attempt_number=attempt_number,
            approved=False,
        )

        messages.success(request, 'Ваш результат отправлен на проверку.')
        return redirect('test_result_detail', result_id=test_result.id)
    else:
        return render(request, 'start_test.html', {
            'test': test,
            'questions': questions,
        })

@login_required
def test_result_detail(request, result_id):
    app_user, role_name = get_current_user(request)
    test_result = get_object_or_404(TestResult, id=result_id, user=app_user)
    return render(request, 'test_result_detail.html', {
        'test_result': test_result,
    })


@login_required
def test_results(request):
    app_user, role_name = get_current_user(request)

    search_query = request.GET.get('search', '').strip()
    sort_by = request.GET.get('sort', 'test_date')
    order = request.GET.get('order', 'desc')

    test_results = TestResult.objects.filter(user=app_user, approved=True).select_related('test').filter(
        Q(test__title__icontains=search_query)
    )

    if order == 'desc':
        sort_by = '-' + sort_by
    test_results = test_results.order_by(sort_by)

    paginator = Paginator(test_results, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'test_results.html', {
        'page_obj': page_obj,
        'role': role_name
    })

@login_required
def request_test_deletion(request, test_id):
    app_user, role_name = get_current_user(request)
    test = get_object_or_404(Test, id=test_id)

    if request.method == 'POST':
        TestDeletionRequest.objects.create(
            test=test,
            requested_by=app_user
        )
        messages.success(request, 'Запрос на удаление теста отправлен администратору.')
        return redirect('test_list')
    else:
        form = TestDeletionRequestForm()

    return render(request, 'request_test_deletion.html', {
        'form': form,
        'test': test,
        'role': role_name
    })

@login_required
def test_deletion_requests(request):
    app_user, role_name = get_current_user(request)
    if role_name != 'admin':
        return HttpResponse('У вас нет доступа к этой странице', status=403)

    deletion_requests = TestDeletionRequest.objects.filter(approved__isnull=True).select_related('test', 'requested_by')

    return render(request, 'test_deletion_requests.html', {
        'deletion_requests': deletion_requests,
        'role': role_name
    })

@login_required
def approve_test_deletion(request, request_id):
    app_user, role_name = get_current_user(request)
    if role_name != 'admin':
        return HttpResponse('У вас нет доступа к этой странице', status=403)

    deletion_request = get_object_or_404(TestDeletionRequest, id=request_id)
    test = deletion_request.test

    if request.method == 'POST':
        if 'approve' in request.POST:
            test.delete()
            deletion_request.approved = True
            messages.success(request, f'Тест "{test.title}" был удалён.')
        elif 'decline' in request.POST:
            deletion_request.approved = False
            messages.info(request, f'Удаление теста "{test.title}" отклонено.')
        deletion_request.save()
        return redirect('test_deletion_requests')

    return render(request, 'approve_test_deletion.html', {
        'deletion_request': deletion_request,
        'test': test,
        'role': role_name
    })

@login_required
def pending_test_results(request):
    app_user, role_name = get_current_user(request)
    if role_name != 'employee':
        return HttpResponse('У вас нет доступа к этой странице', status=403)

    test_results = TestResult.objects.filter(approved=False).select_related('test', 'user')

    return render(request, 'pending_test_results.html', {
        'test_results': test_results,
        'role': role_name
    })

@login_required
def approve_test_result(request, result_id):
    app_user, role_name = get_current_user(request)
    if role_name != 'employee':
        return HttpResponse('У вас нет доступа к этой странице', status=403)

    test_result = get_object_or_404(TestResult, id=result_id)

    if request.method == 'POST':
        if 'approve' in request.POST:
            test_result.approved = True
            test_result.save()
            messages.success(request, 'Результат теста одобрен.')
        elif 'decline' in request.POST:
            test_result.delete()
            messages.info(request, 'Результат теста отклонён и удалён.')
        return redirect('pending_test_results')

    return render(request, 'approve_test_result.html', {
        'test_result': test_result,
        'role': role_name
    })

# Новый view для добавления теста
@login_required
def add_test(request):
    app_user, role_name = get_current_user(request)
    if role_name not in ['employee', 'admin']:
        return HttpResponse('У вас нет доступа', status=403)

    if request.method == 'POST':
        form = AddTestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Тест успешно добавлен')
            return redirect('test_list')
    else:
        form = AddTestForm()

    return render(request, 'add_test.html', {'form': form, 'role': role_name})

# Новый view для просмотра результатов всех пользователей админом
@login_required
def admin_test_results(request):
    app_user, role_name = get_current_user(request)
    if role_name != 'admin':
        return HttpResponse('У вас нет доступа', status=403)

    search_query = request.GET.get('search', '').strip()
    sort_by = request.GET.get('sort', 'test_date')
    order = request.GET.get('order', 'desc')

    test_results = TestResult.objects.select_related('test', 'user').filter(
        Q(test__title__icontains=search_query) |
        Q(user__full_name__icontains=search_query)
    )

    if order == 'desc':
        sort_by = '-' + sort_by

    test_results = test_results.order_by(sort_by)

    paginator = Paginator(test_results, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin_test_results.html', {
        'page_obj': page_obj,
        'role': role_name
    })
# app/views.py (дополнительно к существующему коду)

@login_required
def edit_test(request, test_id):
    app_user, role_name = get_current_user(request)
    if role_name not in ['employee', 'admin']:
        return HttpResponse('Нет доступа', status=403)
    test = get_object_or_404(Test, id=test_id)
    if request.method == 'POST':
        form = AddTestForm(request.POST, instance=test)
        if form.is_valid():
            form.save()
            messages.success(request, 'Тест обновлен')
            return redirect('edit_test', test_id=test_id)
    else:
        form = AddTestForm(instance=test)
    questions = Question.objects.filter(test=test)
    return render(request, 'edit_test.html', {'form': form, 'test': test, 'questions': questions})

@login_required
def add_question(request, test_id):
    app_user, role_name = get_current_user(request)
    if role_name not in ['employee', 'admin']:
        return HttpResponse('Нет доступа', status=403)
    test = get_object_or_404(Test, id=test_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            question.test = test
            question.save()
            messages.success(request, 'Вопрос добавлен')
            return redirect('edit_test', test_id=test_id)
    else:
        form = QuestionForm()
    return render(request, 'add_question.html', {'form': form, 'test': test})

@login_required
def edit_question(request, question_id):
    app_user, role_name = get_current_user(request)
    if role_name not in ['employee', 'admin']:
        return HttpResponse('Нет доступа', status=403)
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Вопрос обновлен')
            return redirect('edit_test', test_id=question.test.id)
    else:
        form = QuestionForm(instance=question)
    answers = Answer.objects.filter(question=question)
    return render(request, 'edit_question.html', {'form': form, 'question': question, 'answers': answers})

@login_required
def add_answer(request, question_id):
    app_user, role_name = get_current_user(request)
    if role_name not in ['employee', 'admin']:
        return HttpResponse('Нет доступа', status=403)
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        form = AnswerForm(request.POST, request.FILES)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.save()
            messages.success(request, 'Ответ добавлен')
            return redirect('edit_question', question_id=question_id)
    else:
        form = AnswerForm()
    return render(request, 'add_answer.html', {'form': form, 'question': question})

@login_required
def edit_answer(request, answer_id):
    app_user, role_name = get_current_user(request)
    if role_name not in ['employee', 'admin']:
        return HttpResponse('Нет доступа', status=403)
    answer = get_object_or_404(Answer, id=answer_id)
    if request.method == 'POST':
        form = AnswerForm(request.POST, request.FILES, instance=answer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ответ обновлен')
            return redirect('edit_question', question_id=answer.question.id)
    else:
        form = AnswerForm(instance=answer)
    return render(request, 'edit_answer.html', {'form': form, 'answer': answer})

# API Views
class UserListAPI(APIView):
    def get(self, request):
        app_users = AppUser.objects.all()
        serializer = UserSerializer(app_users, many=True)
        return Response(serializer.data)

class UserDetailAPI(APIView):
    def get(self, request, user_id):
        try:
            app_user = AppUser.objects.get(id=user_id)
            serializer = UserSerializer(app_user)
            return Response(serializer.data)
        except AppUser.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

class EmployeeListAPI(APIView):
    def get(self, request):
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)

class EmployeeDetailAPI(APIView):
    def get(self, request, employee_id):
        try:
            employee = Employee.objects.get(id=employee_id)
            serializer = EmployeeSerializer(employee)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response({'error': 'Сотрудник не найден'}, status=status.HTTP_404_NOT_FOUND)
