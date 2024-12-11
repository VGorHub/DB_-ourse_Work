# app/forms.py
from django import forms
from .models import AppUser, Employee, TestDeletionRequest, Test, Question, Answer

class UserSelectionForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=AppUser.objects.all(),
        label='Выберите пользователя',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class AppUserForm(forms.ModelForm):
    class Meta:
        model = AppUser
        fields = ['full_name', 'email', 'age']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class AppUserAdminForm(forms.ModelForm):
    class Meta:
        model = AppUser
        fields = ['full_name', 'email', 'age', 'role']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }

class EmployeeForm(forms.ModelForm):
    # Добавляем поля, которые недоступны для редактирования сотрудником, но нужны для корректной валидации
    full_name = forms.CharField(
        max_length=255,
        label='Полное имя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Электронная почта',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    age = forms.IntegerField(
        label='Возраст',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    years_of_experience = forms.IntegerField(label='Стаж работы', required=False, disabled=True)
    position = forms.CharField(label='Должность', required=False, disabled=True)
    salary = forms.DecimalField(label='Зарплата', max_digits=10, decimal_places=2, required=False, disabled=True)

    class Meta:
        model = Employee
        fields = ['full_name', 'email', 'age', 'years_of_experience', 'position', 'salary', 'photo']
        widgets = {
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.user_id:
            self.fields['full_name'].initial = self.instance.user.full_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['age'].initial = self.instance.user.age
            self.fields['years_of_experience'].initial = self.instance.years_of_experience
            self.fields['position'].initial = self.instance.position
            self.fields['salary'].initial = self.instance.salary

    def save(self, commit=True):
        employee = super(EmployeeForm, self).save(commit=False)
        user = employee.user
        user.full_name = self.cleaned_data['full_name']
        user.email = self.cleaned_data['email']
        user.age = self.cleaned_data['age']
        if commit:
            user.save()
            employee.save()
        return employee


class EmployeeAdminForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=255,
        label='Полное имя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Электронная почта',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    age = forms.IntegerField(
        label='Возраст',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        label='Роль',
        choices=AppUser.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Employee
        fields = [
            'full_name',
            'email',
            'age',
            'role',
            'years_of_experience',
            'position',
            'salary',
            'photo'
        ]
        widgets = {
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        super(EmployeeAdminForm, self).__init__(*args, **kwargs)
        # Проверяем, есть ли instance и user
        if self.instance and self.instance.pk and self.instance.user_id:
            self.fields['full_name'].initial = self.instance.user.full_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['age'].initial = self.instance.user.age
            self.fields['role'].initial = self.instance.user.role

    def save(self, commit=True):
        employee = super(EmployeeAdminForm, self).save(commit=False)
        user = employee.user
        user.full_name = self.cleaned_data['full_name']
        user.email = self.cleaned_data['email']
        user.age = self.cleaned_data['age']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
            employee.save()
        return employee


class TestDeletionRequestForm(forms.ModelForm):
    class Meta:
        model = TestDeletionRequest
        fields = []


class AddTestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['title', 'passing_score', 'description', 'time_to_complete']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'passing_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'time_to_complete': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# Форма для вопросов
# app/forms.py
from django import forms
from .models import AppUser, Employee, TestDeletionRequest, Test, Question, Answer

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        # Убираем image
        fields = ['question_text']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        # Убираем image
        fields = ['answer_text', 'is_correct']

