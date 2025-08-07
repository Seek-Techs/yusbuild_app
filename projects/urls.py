from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet, TaskViewSet, MaterialViewSet,
    LabourerViewSet, ReportViewSet, register_user, CustomAuthToken, dashboard_view
)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'materials', MaterialViewSet)
router.register(r'labourers', LabourerViewSet)
router.register(r'reports', ReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', register_user),
    path('login/', CustomAuthToken.as_view()),
    path('dashboard/', dashboard_view),
]
