# app/forms.py
from django import forms
from .models import AppUser, Employee

class UserSelectionForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=AppUser.objects.all(),
        label='Выберите пользователя',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['full_name', 'years_of_experience', 'position', 'salary', 'age', 'photo', 'is_active']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class AppUserForm(forms.ModelForm):
    class Meta:
        model = AppUser
        fields = ['full_name', 'email', 'age', 'is_active']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
