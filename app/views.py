# app/views.py

from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from .models import AppUser, Employee
from django.views.decorators.csrf import csrf_exempt

# Добавляем импорты для DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, EmployeeSerializer


def index(request):
        role = request.session.get('role', 'user')
        user_id = request.session.get('user_id')
        return render(request, 'index.html', {'role': role, 'user_id': user_id})


def set_role(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        if role in ['user', 'admin']:
            request.session['role'] = role
            if role == 'user':
                request.session['user_id'] = 1  # Замените на фактический ID пользователя
            else:
                request.session['user_id'] = None
            messages.success(request, f'Роль установлена: {role}')
        else:
            messages.error(request, 'Неверная роль')
        return redirect('index')
    else:
        return render(request, 'set_role.html')


def user_list(request):
    role = request.session.get('role', 'user')
    if role != 'admin':
        return HttpResponse('У вас нет доступа к этой странице', status=403)

    request.session['last_page'] = request.get_full_path()
    page_size = 10
    page_number = int(request.GET.get('page', 1))
    offset = (page_number - 1) * page_size

    with connection.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM "User"')
        total_users = cursor.fetchone()[0]

        cursor.execute('SELECT * FROM "User" ORDER BY "ID" LIMIT %s OFFSET %s', [page_size, offset])
        columns = [col[0] for col in cursor.description]
        app_users = [dict(zip(columns, row)) for row in cursor.fetchall()]

    total_pages = (total_users + page_size - 1) // page_size

    return render(request, 'user_list.html', {
        'app_users': app_users,
        'role': role,
        'page_number': page_number,
        'total_pages': total_pages
    })


def user_detail(request, user_id):
    role = request.session.get('role', 'user')
    session_user_id = request.session.get('user_id')

    # Проверяем права доступа
    if role != 'admin' and session_user_id != user_id:
        return HttpResponse('У вас нет доступа к этой странице', status=403)

    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM "User" WHERE "ID" = %s', [user_id])
        row = cursor.fetchone()
        if row:
            columns = [col[0] for col in cursor.description]
            app_user = dict(zip(columns, row))
        else:
            return HttpResponse('Пользователь не найден', status=404)

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        age = int(request.POST.get('age'))

        # Создание экземпляра модели для валидации
        app_user_instance = AppUser(
            id=user_id,
            full_name=full_name,
            email=email,
            age=age
        )

        try:
            # Валидация данных
            app_user_instance.full_clean()

            # Обновление данных в базе
            with connection.cursor() as cursor:
                cursor.execute('''
                    UPDATE "User"
                    SET "Full Name" = %s, "Email" = %s, "Age" = %s
                    WHERE "ID" = %s
                ''', [full_name, email, age, user_id])

            messages.success(request, 'Данные пользователя обновлены')
            return redirect('user_detail', user_id=user_id)
        except ValidationError as e:
            # Передача ошибок в шаблон
            errors = e.message_dict
            return render(request, 'user_detail.html', {
                'app_user': app_user,
                'role': role,
                'errors': errors
            })

    return render(request, 'user_detail.html', {'app_user': app_user, 'role': role})


def employee_list(request):
    role = request.session.get('role', 'user')
    if role != 'admin':
        return HttpResponse('У вас нет доступа к этой странице', status=403)

    request.session['last_page'] = request.get_full_path()
    page_size = 10
    page_number = int(request.GET.get('page', 1))
    offset = (page_number - 1) * page_size

    with connection.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM "Employee"')
        total_employees = cursor.fetchone()[0]

        cursor.execute('SELECT * FROM "Employee" ORDER BY "ID" LIMIT %s OFFSET %s', [page_size, offset])
        columns = [col[0] for col in cursor.description]
        employees = [dict(zip(columns, row)) for row in cursor.fetchall()]

    total_pages = (total_employees + page_size - 1) // page_size

    return render(request, 'employee_list.html', {
        'employees': employees,
        'role': role,
        'page_number': page_number,
        'total_pages': total_pages
    })


def employee_detail(request, employee_id):
    role = request.session.get('role', 'user')
    if role != 'admin':
        return HttpResponse('У вас нет доступа к этой странице', status=403)

    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM "Employee" WHERE "ID" = %s', [employee_id])
        row = cursor.fetchone()
        if row:
            columns = [col[0] for col in cursor.description]
            employee = dict(zip(columns, row))
        else:
            return HttpResponse('Сотрудник не найден', status=404)

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        years_of_experience = int(request.POST.get('years_of_experience'))
        position = request.POST.get('position')
        salary = float(request.POST.get('salary'))
        age = int(request.POST.get('age'))
        photo = request.FILES.get('photo')

        # Создание экземпляра модели для валидации
        employee_instance = Employee(
            id=employee_id,
            full_name=full_name,
            years_of_experience=years_of_experience,
            position=position,
            salary=salary,
            age=age,
            photo=photo.read() if photo else employee.get('Photo')
        )

        try:
            # Валидация данных
            employee_instance.full_clean()

            # Обновление данных в базе
            with connection.cursor() as cursor:
                if photo:
                    cursor.execute('''
                        UPDATE "Employee"
                        SET "Full Name" = %s, "Years of Experience" = %s, "Position" = %s,
                            "Salary" = %s, "Age" = %s, "Photo" = %s
                        WHERE "ID" = %s
                    ''', [full_name, years_of_experience, position, salary, age, employee_instance.photo, employee_id])
                else:
                    cursor.execute('''
                        UPDATE "Employee"
                        SET "Full Name" = %s, "Years of Experience" = %s, "Position" = %s,
                            "Salary" = %s, "Age" = %s
                        WHERE "ID" = %s
                    ''', [full_name, years_of_experience, position, salary, age, employee_id])

            messages.success(request, 'Данные сотрудника обновлены')
            return redirect('employee_detail', employee_id=employee_id)
        except ValidationError as e:
            # Передача ошибок в шаблон
            errors = e.message_dict
            return render(request, 'employee_detail.html', {
                'employee': employee,
                'role': role,
                'errors': errors
            })

    return render(request, 'employee_detail.html', {'employee': employee, 'role': role})


def add_user(request):
    role = request.session.get('role', 'user')
    if role != 'admin':
        return HttpResponse('У вас нет доступа к этой странице', status=403)

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        age = int(request.POST.get('age'))

        # Создание экземпляра модели для валидации
        app_user_instance = AppUser(
            full_name=full_name,
            email=email,
            age=age
        )

        try:
            # Валидация данных
            app_user_instance.full_clean()

            # Вставка данных в базу
            with connection.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO "User" ("Full Name", "Email", "Age")
                    VALUES (%s, %s, %s)
                ''', [full_name, email, age])

            messages.success(request, 'Новый пользователь добавлен')
            return redirect('user_list')
        except ValidationError as e:
            errors = e.message_dict
            return render(request, 'add_user.html', {'errors': errors})

    return render(request, 'add_user.html')


def add_employee(request):
    role = request.session.get('role', 'user')
    if role != 'admin':
        return HttpResponse('У вас нет доступа к этой странице', status=403)

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        years_of_experience = int(request.POST.get('years_of_experience'))
        position = request.POST.get('position')
        salary = float(request.POST.get('salary'))
        age = int(request.POST.get('age'))
        photo = request.FILES.get('photo')

        employee_instance = Employee(
            full_name=full_name,
            years_of_experience=years_of_experience,
            position=position,
            salary=salary,
            age=age,
            photo=photo.read() if photo else None
        )

        try:
            employee_instance.full_clean()

            with connection.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO "Employee" ("Full Name", "Years of Experience", "Position", "Salary", "Age", "Photo")
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', [full_name, years_of_experience, position, salary, age, employee_instance.photo])

            messages.success(request, 'Новый сотрудник добавлен')
            return redirect('employee_list')
        except ValidationError as e:
            errors = e.message_dict
            return render(request, 'add_employee.html', {'errors': errors})

    return render(request, 'add_employee.html')


# API Views

class UserListAPI(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM "User"')
            columns = [col[0] for col in cursor.description]
            app_users = [dict(zip(columns, row)) for row in cursor.fetchall()]
        serializer = UserSerializer(app_users, many=True)
        return Response(serializer.data)


class UserDetailAPI(APIView):
    def get(self, request, user_id):
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM "User" WHERE "ID" = %s', [user_id])
            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                app_user = dict(zip(columns, row))
                serializer = UserSerializer(app_user)
                return Response(serializer.data)
            else:
                return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)


class EmployeeListAPI(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM "Employee"')
            columns = [col[0] for col in cursor.description]
            employees = [dict(zip(columns, row)) for row in cursor.fetchall()]
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)


class EmployeeDetailAPI(APIView):
    def get(self, request, employee_id):
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM "Employee" WHERE "ID" = %s', [employee_id])
            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                employee = dict(zip(columns, row))
                serializer = EmployeeSerializer(employee)
                return Response(serializer.data)
            else:
                return Response({'error': 'Сотрудник не найден'}, status=status.HTTP_404_NOT_FOUND)
