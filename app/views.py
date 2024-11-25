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
        employee_id = request.session.get('employee_id')
        return render(request, 'index.html', {'role': role, 'user_id': user_id, 'employee_id': employee_id})


def set_role(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        if role in ['user', 'admin']:
            request.session['role'] = role
            if role == 'user':
                request.session['user_id'] = 1  # Замените на фактический ID пользователя
                request.session['employee_id'] = None
            else:
                # Проверяем, есть ли администратор в базе
                with connection.cursor() as cursor:
                    cursor.execute('SELECT "ID" FROM "Employee" WHERE "Position" = %s LIMIT 1', ['Administrator'])
                    row = cursor.fetchone()
                    if row:
                        employee_id = row[0]
                    else:
                        # Если нет, создаем администратора
                        cursor.execute('''
                            INSERT INTO "Employee" ("Full Name", "Years of Experience", "Position", "Salary", "Age")
                            VALUES (%s, %s, %s, %s, %s) RETURNING "ID"
                        ''', ['Admin', 0, 'Administrator', 0.00, 30])
                        employee_id = cursor.fetchone()[0]
                request.session['employee_id'] = employee_id
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

    # Получаем данные пользователя из базы
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM "User" WHERE "ID" = %s', [user_id])
        row = cursor.fetchone()
        if row:
            columns = [col[0] for col in cursor.description]
            app_user = dict(zip(columns, row))
        else:
            return HttpResponse('Пользователь не найден', status=404)

    if request.method == 'POST':
        full_name = request.POST.get('full_name').strip()
        email = request.POST.get('email').strip()
        age_input = request.POST.get('age').strip()

        errors = {}

        # Валидация данных

        # Проверка полноты данных
        if not full_name:
            errors['full_name'] = ['Полное имя обязательно.']
        if not email:
            errors['email'] = ['Email обязателен.']
        if not age_input:
            errors['age'] = ['Возраст обязателен.']

        # Проверка возраста
        try:
            age = int(age_input)
            if age <= 0:
                errors['age'] = ['Возраст должен быть положительным числом.']
        except ValueError:
            errors['age'] = ['Возраст должен быть числом.']

        # Проверка уникальности email
        if email:
            with connection.cursor() as cursor_check:
                cursor_check.execute('SELECT "ID" FROM "User" WHERE "Email" = %s AND "ID" != %s', [email, user_id])
                if cursor_check.fetchone():
                    errors['email'] = ['Пользователь с таким Email уже существует.']

        if errors:
            return render(request, 'user_detail.html', {
                'app_user': app_user,
                'role': role,
                'errors': errors
            })

        # Обновление данных в базе
        with connection.cursor() as cursor_update:
            cursor_update.execute('''
                UPDATE "User"
                SET "Full Name" = %s, "Email" = %s, "Age" = %s
                WHERE "ID" = %s
            ''', [full_name, email, age, user_id])

        messages.success(request, 'Данные пользователя обновлены')
        return redirect('user_detail', user_id=user_id)

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
    session_employee_id = request.session.get('employee_id')

    # Проверяем права доступа
    if role != 'admin':
        return HttpResponse('У вас нет доступа к этой странице', status=403)

    # Получаем данные сотрудника из базы
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM "Employee" WHERE "ID" = %s', [employee_id])
        row = cursor.fetchone()
        if row:
            columns = [col[0] for col in cursor.description]
            employee = dict(zip(columns, row))
        else:
            return HttpResponse('Сотрудник не найден', status=404)

    if request.method == 'POST':
        full_name = request.POST.get('full_name').strip()
        years_of_experience_input = request.POST.get('years_of_experience').strip()
        position = request.POST.get('position').strip()
        salary_input = request.POST.get('salary').strip()
        age_input = request.POST.get('age').strip()
        photo_file = request.FILES.get('photo')

        errors = {}

        # Валидация данных

        # Проверка полноты данных
        if not full_name:
            errors['full_name'] = ['Полное имя обязательно.']
        if not years_of_experience_input:
            errors['years_of_experience'] = ['Стаж работы обязателен.']
        if not position:
            errors['position'] = ['Должность обязательна.']
        if not salary_input:
            errors['salary'] = ['Зарплата обязательна.']
        if not age_input:
            errors['age'] = ['Возраст обязателен.']

        # Проверка числовых полей
        try:
            years_of_experience = int(years_of_experience_input)
            if years_of_experience < 0:
                errors['years_of_experience'] = ['Стаж работы не может быть отрицательным.']
        except ValueError:
            errors['years_of_experience'] = ['Стаж работы должен быть числом.']

        try:
            salary = float(salary_input)
            if salary < 0:
                errors['salary'] = ['Зарплата не может быть отрицательной.']
        except ValueError:
            errors['salary'] = ['Зарплата должна быть числом.']

        try:
            age = int(age_input)
            if age <= 0:
                errors['age'] = ['Возраст должен быть положительным числом.']
        except ValueError:
            errors['age'] = ['Возраст должен быть числом.']

        # Логическая проверка: стаж не может превышать возраст
        if 'years_of_experience' not in errors and 'age' not in errors:
            if years_of_experience > age:
                errors['years_of_experience'] = ['Стаж работы не может превышать возраст.']

        # Обработка фотографии
        if photo_file:
            try:
                photo = photo_file.read()
            except Exception as e:
                errors['photo'] = ['Не удалось загрузить фотографию.']
        else:
            photo = employee.get('Photo')  # Оставляем старую фотографию

        if errors:
            return render(request, 'employee_detail.html', {
                'employee': employee,
                'role': role,
                'errors': errors
            })

        # Обновление данных в базе
        with connection.cursor() as cursor_update:
            if photo_file:
                cursor_update.execute('''
                    UPDATE "Employee"
                    SET "Full Name" = %s, "Years of Experience" = %s, "Position" = %s,
                        "Salary" = %s, "Age" = %s, "Photo" = %s
                    WHERE "ID" = %s
                ''', [full_name, years_of_experience, position, salary, age, photo, employee_id])
            else:
                cursor_update.execute('''
                    UPDATE "Employee"
                    SET "Full Name" = %s, "Years of Experience" = %s, "Position" = %s,
                        "Salary" = %s, "Age" = %s
                    WHERE "ID" = %s
                ''', [full_name, years_of_experience, position, salary, age, employee_id])

        messages.success(request, 'Данные профиля обновлены')
        return redirect('employee_detail', employee_id=employee_id)

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
