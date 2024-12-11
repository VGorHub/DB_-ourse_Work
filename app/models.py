# app/models.py
from django.db import models
from django.core.exceptions import ValidationError

class AppUser(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
        ('employee', 'Employee'),
    ]

    id = models.AutoField(primary_key=True, db_column='ID')
    full_name = models.CharField(max_length=255, db_column='Full Name')
    email = models.EmailField(max_length=254, unique=True, db_column='Email')
    age = models.PositiveIntegerField(db_column='Age')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user', db_column='Role')

    class Meta:
        db_table = 'User'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def clean(self):
        if self.age <= 0:
            raise ValidationError({'age': 'Возраст должен быть положительным числом.'})

    def __str__(self):
        return self.full_name

class Employee(models.Model):
    user = models.OneToOneField(AppUser, on_delete=models.CASCADE, db_column='User ID')
    years_of_experience = models.PositiveIntegerField(db_column='Years of Experience')
    position = models.CharField(max_length=255, db_column='Position')
    salary = models.DecimalField(max_digits=10, decimal_places=2, db_column='Salary')
    photo = models.ImageField(null=True, blank=True, upload_to='employee_photos/', db_column='Photo')
    is_fired = models.BooleanField(default=False, db_column='Is Fired')  # новое поле

    class Meta:
        db_table = 'Employee'
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def clean(self):
        errors = {}
        if self.years_of_experience < 0:
            errors['years_of_experience'] = 'Стаж работы не может быть отрицательным.'
        if self.salary < 0:
            errors['salary'] = 'Зарплата не может быть отрицательной.'
        if self.years_of_experience > self.user.age:
            errors['years_of_experience'] = 'Стаж работы не может превышать возраст.'
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.user.full_name

class Test(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID')
    title = models.CharField(max_length=255, db_column='Title')
    passing_score = models.PositiveIntegerField(db_column='Passing Score')
    description = models.TextField(null=True, blank=True, db_column='Description')
    time_to_complete = models.PositiveIntegerField(db_column='Time to Complete')

    class Meta:
        db_table = 'Test'
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'

    def clean(self):
        errors = {}
        if self.passing_score < 0:
            errors['passing_score'] = 'Проходной балл не может быть отрицательным.'
        if self.time_to_complete <= 0:
            errors['time_to_complete'] = 'Время на прохождение должно быть положительным числом.'
        if errors:
            raise ValidationError(errors)

class Question(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID')
    test = models.ForeignKey('Test', on_delete=models.CASCADE, db_column='Test ID')
    question_text = models.TextField(db_column='Question Text')
    image = models.BinaryField(null=True, blank=True, db_column='Image for the Question')

    class Meta:
        db_table = 'Question'
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

class Answer(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID')
    question = models.ForeignKey('Question', on_delete=models.CASCADE, db_column='Question ID')
    answer_text = models.TextField(db_column='Answer Text')
    is_correct = models.BooleanField(db_column='Correct Answer')
    image = models.BinaryField(null=True, blank=True, db_column='Image for the Answer')

    class Meta:
        db_table = 'Answer'
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

class TestResult(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID')
    user = models.ForeignKey('AppUser', on_delete=models.CASCADE, db_column='User ID')
    # Изменено: при удалении теста результаты не удаляются, test становится NULL
    test = models.ForeignKey('Test', on_delete=models.SET_NULL, null=True, blank=True, db_column='Test ID')
    employee = models.ForeignKey('Employee', null=True, blank=True, on_delete=models.CASCADE, db_column='Employee ID')
    test_date = models.DateField(db_column='Test Date')
    score_achieved = models.PositiveIntegerField(db_column='Score Achieved')
    status = models.CharField(max_length=20, db_column='Status')
    attempt_number = models.PositiveIntegerField(db_column='Attempt Number')
    approved = models.BooleanField(null=True, db_column='Approved')

    class Meta:
        db_table = 'TestResult'
        verbose_name = 'Результат Теста'
        verbose_name_plural = 'Результаты Тестов'

    def clean(self):
        errors = {}
        if self.status not in ['passed', 'failed', 'in_progress']:
            errors['status'] = 'Недопустимое значение статуса.'
        num_questions = Question.objects.filter(test=self.test).count() if self.test else 0
        if self.score_achieved > num_questions:
            errors['score_achieved'] = 'Набранный балл не может превышать количество вопросов в тесте.'
        if self.attempt_number <= 0:
            errors['attempt_number'] = 'Номер попытки должен быть положительным числом.'
        if errors:
            raise ValidationError(errors)


class TestDeletionRequest(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID')
    test = models.ForeignKey('Test', on_delete=models.CASCADE, db_column='Test ID')
    requested_by = models.ForeignKey('AppUser', on_delete=models.CASCADE, db_column='Requested By')
    requested_at = models.DateTimeField(auto_now_add=True, db_column='Requested At')
    approved = models.BooleanField(null=True, db_column='Approved')

    class Meta:
        db_table = 'TestDeletionRequest'
        verbose_name = 'Запрос на удаление теста'
        verbose_name_plural = 'Запросы на удаление тестов'

    def __str__(self):
        return f"Запрос на удаление теста {self.test.title} от {self.requested_by.full_name}"
