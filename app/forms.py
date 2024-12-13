# app/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Value
from django.db.models.functions import Concat

from .models import AppUser, Employee, TestDeletionRequest, Test, Question, Answer

class UserSelectionForm(forms.Form):
    """
    Форма выбора пользователя для входа (имитация логина).
    """
    user_or_employee = forms.ChoiceField(
        label="Выберите пользователя или сотрудника",
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Объединяем пользователей и сотрудников
        app_users = AppUser.objects.annotate(
            label=Concat('full_name', Value(' (Пользователь)'))
        ).values_list('id', 'label')

        employees = Employee.objects.annotate(
            label=Concat('full_name', Value(' (Сотрудник)'))
        ).values_list('id', 'label')

        combined_choices = list(app_users) + list(employees)
        self.fields['user_or_employee'].choices = combined_choices


class AppUserForm(forms.ModelForm):
    """
    Форма редактирования данных обычного пользователя.
    """
    class Meta:
        model = AppUser
        fields = ['full_name', 'email', 'age']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if AppUser.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует.")
        return email


class AppUserAdminForm(forms.ModelForm):
    """
    Форма редактирования данных пользователя с правами админа.
    """
    class Meta:
        model = AppUser
        fields = ['full_name', 'email', 'age']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if AppUser.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует.")
        return email


class EmployeeForm(forms.ModelForm):
    """
    Форма редактирования данных сотрудника (для роли 'employee').
    """
    class Meta:
        model = Employee
        fields = ['full_name', 'email', 'age', 'years_of_experience', 'position', 'salary', 'photo']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Employee.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise ValidationError("Сотрудник с таким email уже существует.")
        return email


class EmployeeAdminForm(forms.ModelForm):
    """
    Форма редактирования данных сотрудника для админа, включая роль.
    """
    class Meta:
        model = Employee
        fields = ['full_name', 'email', 'age', 'role', 'years_of_experience', 'position', 'salary', 'photo']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Employee.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise ValidationError("Сотрудник с таким email уже существует.")
        return email


class TestDeletionRequestForm(forms.ModelForm):
    """
    Форма запроса на удаление теста.
    """
    class Meta:
        model = TestDeletionRequest
        fields = []


class AddTestForm(forms.ModelForm):
    """
    Форма добавления/редактирования теста.
    """
    class Meta:
        model = Test
        fields = ['title', 'passing_score', 'description', 'time_to_complete']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'passing_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'time_to_complete': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class QuestionForm(forms.ModelForm):
    """
    Форма добавления/редактирования вопроса.
    """
    class Meta:
        model = Question
        fields = ['question_text', 'image']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'})
        }


class AnswerForm(forms.ModelForm):
    """
    Форма добавления/редактирования ответа.
    """
    class Meta:
        model = Answer
        fields = ['answer_text', 'is_correct', 'image']
        widgets = {
            'answer_text': forms.Textarea(attrs={'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'})
        }

    def clean(self):
        cleaned_data = super().clean()
        is_correct = cleaned_data.get('is_correct', False)
        question = self.instance.question if self.instance.pk else None

        # Если новый ответ или редактирование ответа
        # Если is_correct = True, проверяем, что нет другого правильного ответа
        if is_correct and question:
            # Ищем другие правильные ответы
            other_correct = question.answers.filter(is_correct=True).exclude(pk=self.instance.pk)
            if other_correct.exists():
                raise ValidationError("У данного вопроса уже есть правильный ответ.")
        return cleaned_data
