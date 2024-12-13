# app/serializers.py
from rest_framework import serializers
from .models import AppUser, Employee

class UserSerializer(serializers.Serializer):
    ID = serializers.IntegerField(source='id')
    Full_Name = serializers.CharField(source='full_name')
    Email = serializers.EmailField(source='email')
    Age = serializers.IntegerField(source='age')

class EmployeeSerializer(serializers.Serializer):
    ID = serializers.IntegerField(source='id')
    Full_Name = serializers.CharField(source='full_name')
    Email = serializers.EmailField(source='email')
    Age = serializers.IntegerField(source='age')
    Years_of_Experience = serializers.IntegerField(source='years_of_experience')
    Position = serializers.CharField(source='position')
    Salary = serializers.DecimalField(max_digits=10, decimal_places=2, source='salary')
    Photo = serializers.CharField(source='photo', allow_null=True, required=False)
