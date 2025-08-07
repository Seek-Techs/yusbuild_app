from django.shortcuts import render

from rest_framework import viewsets
from .models import Project, Task, Material, Labourer, Report
from .serializers import (
    ProjectSerializer, TaskSerializer, MaterialSerializer,
    LabourerSerializer, ReportSerializer
)
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from .permissions import IsManager
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Show only projects assigned to the current user
        return Project.objects.filter(users=self.request.user)

    def perform_create(self, serializer):
        # Auto-assign creator to the project
        project = serializer.save()
        project.users.add(self.request.user)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()  # ✅ Add this
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project', 'completed']  # ✅ filtering options

    def get_queryset(self):
        return Task.objects.filter(project__users=self.request.user)

    def perform_create(self, serializer):
        project = serializer.validated_data['project']
        if self.request.user not in project.users.all():
            raise PermissionDenied("You can't add tasks to a project you're not assigned to.")
        serializer.save()


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()  # ✅ Add this
    serializer_class = MaterialSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project', 'name']

    def get_queryset(self):
        return Material.objects.filter(project__users=self.request.user)

    def perform_create(self, serializer):
        project = serializer.validated_data['project']
        if self.request.user not in project.users.all():
            raise PermissionDenied("You can't add materials to a project you're not assigned to.")
        serializer.save()

class LabourerViewSet(viewsets.ModelViewSet):
    queryset = Labourer.objects.all()  # ✅ Add this
    serializer_class = LabourerSerializer
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['project', 'completed']

    def get_queryset(self):
        return Labourer.objects.filter(project__users=self.request.user)

    def perform_create(self, serializer):
        project = serializer.validated_data['project']
        if self.request.user not in project.users.all():
            raise PermissionDenied("You can't add workers to a project you're not assigned to.")
        serializer.save()

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()  # ✅ Add this
    serializer_class = ReportSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project', 'date']

    def get_queryset(self):
        return Report.objects.filter(project__users=self.request.user)

    def perform_create(self, serializer):
        project = serializer.validated_data['project']
        if self.request.user not in project.users.all():
            raise PermissionDenied("You can't add materials to a project you're not assigned to.")
        serializer.save()

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'DELETE']:
            return [IsManager()]
        return super().get_permissions()

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password)
    token = Token.objects.create(user=user)
    return Response({'token': token.key}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    user = request.user
    projects = Project.objects.filter(users=user)

    data = []
    for project in projects:
        recent_reports = project.reports.order_by('-date')[:3]
        team = [u.username for u in project.users.all()]

        data.append({
            'id': project.id,
            'name': project.name,
            'location': project.location,
            'progress': project.progress,
            'team': team,
            'recent_reports': ReportSerializer(recent_reports, many=True, context={'request': request}).data
        })

    return Response({'projects': data})

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'username': user.username,
            'role': user.profile.role  # only if Profile model exists
        })