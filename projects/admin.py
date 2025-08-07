from django.contrib import admin

from .models import Project, Task, Material, Labourer, Report, Profile # the project model

admin.site.register(Project) # First model in the admin panel created in the projects app model.py
admin.site.register(Task)
admin.site.register(Material)
admin.site.register(Labourer)
admin.site.register(Report)
admin.site.register(Profile)  # Register the Profile model to the admin panel