# app/serializers.py
from rest_framework import serializers

class UserSerializer(serializers.Serializer):
    ID = serializers.IntegerField()
    Full_Name = serializers.CharField(max_length=255, source='full_name')
    Email = serializers.EmailField(source='email')
    Age = serializers.IntegerField(source='age')

class EmployeeSerializer(serializers.Serializer):
    ID = serializers.IntegerField()
    User_ID = serializers.IntegerField(source='user.id')
    Full_Name = serializers.CharField(source='user.full_name')
    Email = serializers.EmailField(source='user.email')
    Age = serializers.IntegerField(source='user.age')
    Years_of_Experience = serializers.IntegerField(source='years_of_experience')
    Position = serializers.CharField(max_length=255)
    Salary = serializers.DecimalField(max_digits=10, decimal_places=2)
    Photo = serializers.CharField(allow_null=True, required=False)
