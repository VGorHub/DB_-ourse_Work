# app/serializers.py
from rest_framework import serializers

class UserSerializer(serializers.Serializer):
    ID = serializers.IntegerField()
    Full_Name = serializers.CharField(max_length=255, source='Full Name')
    Email = serializers.EmailField()
    Age = serializers.IntegerField()

class EmployeeSerializer(serializers.Serializer):
    ID = serializers.IntegerField()
    Full_Name = serializers.CharField(max_length=255, source='Full Name')
    Years_of_Experience = serializers.IntegerField(source='Years of Experience')
    Position = serializers.CharField(max_length=255)
    Salary = serializers.DecimalField(max_digits=10, decimal_places=2)
    Age = serializers.IntegerField()
    Photo = serializers.CharField(allow_null=True, required=False)
