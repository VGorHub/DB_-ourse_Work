# app/forms.py
from django import forms
from .models import AppUser, Employee, Role

class RoleSelectionForm(forms.Form):
    role = forms.ModelChoiceField(queryset=Role.objects.all(), label='Выберите роль')

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['full_name', 'years_of_experience', 'position', 'salary', 'age', 'photo', 'is_active']

class AppUserForm(forms.ModelForm):
    class Meta:
        model = AppUser
        fields = ['full_name', 'email', 'age', 'is_active']
