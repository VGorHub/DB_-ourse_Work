# app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from .models import AppUser, Employee, Role
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from .forms import AppUserForm, EmployeeForm, RoleSelectionForm
from django.utils.decorators import method_decorator

# Добавляем импорты для DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, EmployeeSerializer

def index(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('set_role')
    try:
        app_user = AppUser.objects.get(id=user_id)
        role_name = app_user.role.name
    except AppUser.DoesNotExist:
        role_name = 'user'
    return render(request, 'index.html', {'role': role_name, 'user_id': user_id})

def set_role(request):
    if request.method == 'POST':
        form = RoleSelectionForm(request.POST)
        if form.is_valid():
            role_name = form.cleaned_data['role']
            try:
                role = Role.objects.get(name=role_name)
            except Role.DoesNotExist:
                messages.error(request, 'Неверная роль')
                return redirect('set_role')

            app_user = AppUser.objects.filter(role=role).first()
            if not app_user:
                messages.error(request, f'Нет пользователя с ролью {role_name}')
                return redirect('set_role')

            request.session['user_id'] = app_user.id
            messages.success(request, f'Вы вошли как {role_name}')
            return redirect('index')
    else:
        form = RoleSelectionForm()
    return render(request, 'set_role.html', {'form': form})

def get_user_role(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return None, None
    try:
        app_user = AppUser.objects.get(id=user_id)
        return app_user, app_user.role.name
    except AppUser.DoesNotExist:
        return None, None

def require_role(role_name):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            app_user, user_role = get_user_role(request)
            if not app_user:
                return redirect('set_role')
            if user_role != role_name:
                return HttpResponse('У вас нет доступа к этой странице', status=403)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

@require_role('admin')
def user_list(request):
    app_user, role_name = get_user_role(request)
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'id')
    order = request.GET.get('order', 'asc')

    user_list = AppUser.objects.filter(
        models.Q(full_name__icontains=search_query) | models.Q(email__icontains=search_query)
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



def user_detail(request, user_id):
    app_user, role_name = get_user_role(request)
    if not app_user:
        return redirect('set_role')

    target_user = get_object_or_404(AppUser, id=user_id)

    if role_name != 'admin' and app_user.id != target_user.id:
        return HttpResponse('У вас нет доступа к этой странице', status=403)

    if request.method == 'POST':
        form = AppUserForm(request.POST, instance=target_user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные пользователя обновлены')
            return redirect('user_detail', user_id=user_id)
    else:
        form = AppUserForm(instance=target_user)

    return render(request, 'user_detail.html', {
        'form': form,
        'app_user': target_user,
        'role': role_name
    })

@require_role('admin')
def employee_list(request):
    app_user, role_name = get_user_role(request)
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'id')
    order = request.GET.get('order', 'asc')

    employee_list = Employee.objects.filter(full_name__icontains=search_query)
    if order == 'desc':
        sort_by = '-' + sort_by
    employee_list = employee_list.order_by(sort_by)

    paginator = Paginator(employee_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'employee_list.html', {
        'page_obj': page_obj,
        'role': role_name
    })

@require_role('admin')
def employee_detail(request, employee_id):
    app_user, role_name = get_user_role(request)

    employee = get_object_or_404(Employee, id=employee_id)

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные сотрудника обновлены')
            return redirect('employee_detail', employee_id=employee_id)
    else:
        form = EmployeeForm(instance=employee)

    return render(request, 'employee_detail.html', {
        'form': form,
        'employee': employee,
        'role': role_name
    })

@require_role('admin')
def add_user(request):
    app_user, role_name = get_user_role(request)

    if request.method == 'POST':
        form = AppUserForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            role_user = Role.objects.get(name='user')
            new_user.role = role_user
            new_user.save()
            messages.success(request, 'Новый пользователь добавлен')
            return redirect('user_list')
    else:
        form = AppUserForm()

    return render(request, 'add_user.html', {'form': form})

@require_role('admin')
def add_employee(request):
    app_user, role_name = get_user_role(request)

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Новый сотрудник добавлен')
            return redirect('employee_list')
    else:
        form = EmployeeForm()

    return render(request, 'add_employee.html', {'form': form})

@require_role('admin')
def delete_user(request, user_id):
    app_user, role_name = get_user_role(request)

    target_user = get_object_or_404(AppUser, id=user_id)
    target_user.delete()
    messages.success(request, 'Пользователь удалён')
    return redirect('user_list')

@require_role('admin')
def delete_employee(request, employee_id):
    app_user, role_name = get_user_role(request)

    employee = get_object_or_404(Employee, id=employee_id)
    employee.delete()
    messages.success(request, 'Сотрудник удалён')
    return redirect('employee_list')

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
