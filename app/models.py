# app/models.py
from django.db import models
from django.core.exceptions import ValidationError

# Общие константы для выбора ролей
ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('user', 'User'),
    ('employee', 'Employee'),
]

# Общие константы для статуса теста
TEST_STATUS_CHOICES = [
    ('passed', 'Пройден'),
    ('failed', 'Не пройден'),
    ('in_progress', 'В процессе'),
]


class AppUser(models.Model):
    """
    Модель пользователя приложения без поля role.
    """
    id = models.AutoField(primary_key=True, db_column='ID')
    full_name = models.CharField(max_length=255, db_column='Full Name')
    email = models.EmailField(max_length=254, unique=True, db_column='Email')
    age = models.PositiveIntegerField(db_column='Age')

    class Meta:
        db_table = 'User'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def clean(self):
        super().clean()
        if self.age <= 0:
            raise ValidationError({'age': 'Возраст должен быть положительным числом.'})

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class Employee(models.Model):
    """
    Модель сотрудника.
    """
    id = models.AutoField(primary_key=True, db_column='ID')
    full_name = models.CharField(max_length=255, db_column='Full Name')
    email = models.EmailField(max_length=254, unique=True, db_column='Email')
    age = models.PositiveIntegerField(db_column='Age')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee', db_column='Role')
    years_of_experience = models.PositiveIntegerField(db_column='Years of Experience')
    position = models.CharField(max_length=255, db_column='Position')
    salary = models.DecimalField(max_digits=10, decimal_places=2, db_column='Salary')
    photo = models.ImageField(null=True, blank=True, upload_to='employee_photos/', db_column='Photo')
    is_fired = models.BooleanField(default=False, db_column='Is Fired')

    class Meta:
        db_table = 'Employee'
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def clean(self):
        super().clean()
        errors = {}
        if self.years_of_experience < 0:
            errors['years_of_experience'] = 'Стаж работы не может быть отрицательным.'
        if self.salary < 0:
            errors['salary'] = 'Зарплата не может быть отрицательной.'
        if self.years_of_experience > self.age:
            errors['years_of_experience'] = 'Стаж работы не может превышать возраст.'
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.full_name} ({self.position})"


class Test(models.Model):
    """
    Модель теста.
    """
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
        super().clean()
        errors = {}
        if self.passing_score < 0:
            errors['passing_score'] = 'Проходной балл не может быть отрицательным.'
        if self.time_to_complete <= 0:
            errors['time_to_complete'] = 'Время на прохождение должно быть положительным числом.'
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.title


class Question(models.Model):
    """
    Модель вопроса к тесту.
    """
    id = models.AutoField(primary_key=True, db_column='ID')
    test = models.ForeignKey('Test', on_delete=models.CASCADE, db_column='Test ID', related_name='questions')
    question_text = models.TextField(db_column='Question Text')
    image = models.ImageField(null=True, blank=True, upload_to='question_images/', db_column='Image for the Question')

    class Meta:
        db_table = 'Question'
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return self.question_text


class Answer(models.Model):
    """
    Модель ответа на вопрос.
    """
    question = models.ForeignKey('Question', on_delete=models.CASCADE, db_column='Question ID', related_name='answers')
    answer_text = models.TextField(db_column='Answer Text')
    is_correct = models.BooleanField(db_column='Correct Answer', default=False)
    image = models.ImageField(null=True, blank=True, upload_to='answer_images/', db_column='Image for the Answer')

    class Meta:
        db_table = 'Answer'
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def clean(self):
        super().clean()
        if self.is_correct and self.question:
            # Проверяем, есть ли уже правильный ответ у этого вопроса
            other_correct = Answer.objects.filter(question=self.question, is_correct=True).exclude(pk=self.pk)
            if other_correct.exists():
                raise ValidationError("У данного вопроса уже есть правильный ответ.")

    def __str__(self):
        prefix = "[Верный]" if self.is_correct else "[Неверный]"
        return f"{prefix} {self.answer_text}"


class TestResult(models.Model):
    """
    Модель результата прохождения теста пользователем.
    """
    id = models.AutoField(primary_key=True, db_column='ID')
    user = models.ForeignKey('AppUser', on_delete=models.CASCADE, db_column='User ID', related_name='test_results')
    test = models.ForeignKey('Test', on_delete=models.SET_NULL, null=True, blank=True, db_column='Test ID', related_name='results')
    employee = models.ForeignKey('Employee', null=True, blank=True, on_delete=models.CASCADE, db_column='Employee ID', related_name='test_results')
    test_date = models.DateField(db_column='Test Date')
    score_achieved = models.PositiveIntegerField(db_column='Score Achieved')
    status = models.CharField(max_length=20, db_column='Status', choices=TEST_STATUS_CHOICES)
    attempt_number = models.PositiveIntegerField(db_column='Attempt Number')
    approved = models.BooleanField(null=True, db_column='Approved')

    class Meta:
        db_table = 'TestResult'
        verbose_name = 'Результат Теста'
        verbose_name_plural = 'Результаты Тестов'

    def clean(self):
        super().clean()
        errors = {}
        if self.status not in dict(TEST_STATUS_CHOICES):
            errors['status'] = 'Недопустимое значение статуса.'
        num_questions = self.test.questions.count() if self.test else 0
        if self.score_achieved > num_questions:
            errors['score_achieved'] = 'Набранный балл не может превышать количество вопросов в тесте.'
        if self.attempt_number <= 0:
            errors['attempt_number'] = 'Номер попытки должен быть положительным числом.'
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        test_title = self.test.title if self.test else "Тест удален"
        return f"Результат: {test_title} для {self.user.full_name}, статус: {self.status}"


class TestDeletionRequest(models.Model):
    """
    Модель запроса на удаление теста.
    """
    id = models.AutoField(primary_key=True, db_column='ID')
    test = models.ForeignKey('Test', on_delete=models.CASCADE, db_column='Test ID', related_name='deletion_requests')
    requested_by = models.ForeignKey('AppUser', on_delete=models.CASCADE, db_column='Requested By', related_name='test_deletion_requests')
    requested_at = models.DateTimeField(auto_now_add=True, db_column='Requested At')
    approved = models.BooleanField(null=True, db_column='Approved')

    class Meta:
        db_table = 'TestDeletionRequest'
        verbose_name = 'Запрос на удаление теста'
        verbose_name_plural = 'Запросы на удаление тестов'

    def __str__(self):
        return f"Запрос на удаление теста '{self.test.title}' от {self.requested_by.full_name}"
