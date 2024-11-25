# myapp/forms.py
from django import forms

class SetRoleForm(forms.Form):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES)
