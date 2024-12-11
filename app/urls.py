# app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('set_user/', views.set_user, name='set_user'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/<int:employee_id>/', views.employee_detail, name='employee_detail'),
    path('employees/delete/<int:employee_id>/', views.delete_employee, name='delete_employee'),

    # Новые маршруты для увольнения и полного удаления сотрудника
    path('employees/fire/<int:employee_id>/', views.fire_employee, name='fire_employee'),
    path('employees/delete_from_db/<int:employee_id>/', views.delete_fired_employee, name='delete_fired_employee'),

    path('users/add/', views.add_user, name='add_user'),
    path('employees/add/', views.add_employee, name='add_employee'),

    path('tests/', views.test_list, name='test_list'),
    path('tests/start/<int:test_id>/', views.start_test, name='start_test'),
    path('tests/result/<int:result_id>/', views.test_result_detail, name='test_result_detail'),
    path('tests/results/', views.test_results, name='test_results'),
    path('tests/request_delete/<int:test_id>/', views.request_test_deletion, name='request_test_deletion'),

    # Новый маршрут для добавления теста сотрудником/админом
    path('tests/add/', views.add_test, name='add_test'),

    # Новый маршрут для просмотра результатов тестов админом
    path('admin1/test_results/', views.admin_test_results, name='admin_test_results'),

    path('admin1/test_deletion_requests/', views.test_deletion_requests, name='test_deletion_requests'),
    path('admin1/approve_test_deletion/<int:request_id>/', views.approve_test_deletion, name='approve_test_deletion'),

    path('employee/pending_test_results/', views.pending_test_results, name='pending_test_results'),
    path('employee/approve_test_result/<int:result_id>/', views.approve_test_result, name='approve_test_result'),

    # API
    path('api/users/', views.UserListAPI.as_view(), name='api_user_list'),
    path('api/users/<int:user_id>/', views.UserDetailAPI.as_view(), name='api_user_detail'),
    path('api/employees/', views.EmployeeListAPI.as_view(), name='api_employee_list'),
    path('api/employees/<int:employee_id>/', views.EmployeeDetailAPI.as_view(), name='api_employee_detail'),
    # Редактирование тестов (только для employee/admin)
    path('tests/edit/<int:test_id>/', views.edit_test, name='edit_test'),
    path('tests/<int:test_id>/add_question/', views.add_question, name='add_question'),
    path('question/edit/<int:question_id>/', views.edit_question, name='edit_question'),
    path('question/<int:question_id>/add_answer/', views.add_answer, name='add_answer'),
    path('answer/edit/<int:answer_id>/', views.edit_answer, name='edit_answer'),
]
