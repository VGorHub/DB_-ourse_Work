# app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Web Views
    path('', views.index, name='index'),
    path('set_role/', views.set_role, name='set_role'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),  # Добавлено
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/<int:employee_id>/', views.employee_detail, name='employee_detail'),
    path('employees/delete/<int:employee_id>/', views.delete_employee, name='delete_employee'),  # Добавлено
    path('users/add/', views.add_user, name='add_user'),
    path('employees/add/', views.add_employee, name='add_employee'),

    # API Views
    path('api/users/', views.UserListAPI.as_view(), name='api_user_list'),
    path('api/users/<int:user_id>/', views.UserDetailAPI.as_view(), name='api_user_detail'),
    path('api/employees/', views.EmployeeListAPI.as_view(), name='api_employee_list'),
    path('api/employees/<int:employee_id>/', views.EmployeeDetailAPI.as_view(), name='api_employee_detail'),
]
