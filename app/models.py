# app/models.py
from django.db import models
from django.core.exceptions import ValidationError

class AppUser(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID')
    full_name = models.CharField(max_length=255, db_column='Full Name')
    email = models.EmailField(max_length=254, unique=True, db_column='Email')
    age = models.PositiveIntegerField(db_column='Age')

    class Meta:
        db_table = 'User'  # Имя таблицы в БД остаётся 'User'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def clean(self):
        if self.age <= 0:
            raise ValidationError({'age': 'Возраст должен быть положительным числом.'})

class Employee(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID')
    full_name = models.CharField(max_length=255, db_column='Full Name')
    years_of_experience = models.PositiveIntegerField(db_column='Years of Experience')
    position = models.CharField(max_length=255, db_column='Position')
    salary = models.DecimalField(max_digits=10, decimal_places=2, db_column='Salary')
    age = models.PositiveIntegerField(db_column='Age')
    photo = models.BinaryField(null=True, blank=True, db_column='Photo')

    class Meta:
        db_table = 'Employee'
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def clean(self):
        errors = {}
        if self.age <= 0:
            errors['age'] = 'Возраст должен быть положительным числом.'
        if self.years_of_experience < 0:
            errors['years_of_experience'] = 'Стаж работы не может быть отрицательным.'
        if self.salary < 0:
            errors['salary'] = 'Зарплата не может быть отрицательной.'
        if self.years_of_experience > self.age:
            errors['years_of_experience'] = 'Стаж работы не может превышать возраст.'
        if errors:
            raise ValidationError(errors)
