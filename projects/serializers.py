from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Project, Task, Material, Labourer, Report

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'

class LabourerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Labourer
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=False
    )
    tasks = TaskSerializer(many=True, read_only=True)
    materials = MaterialSerializer(many=True, read_only=True)
    labourers = LabourerSerializer(many=True, read_only=True)
    reports = ReportSerializer(many=True, read_only=True)
    progress = serializers.ReadOnlyField()

    class Meta:
        model = Project
        fields = '__all__'
