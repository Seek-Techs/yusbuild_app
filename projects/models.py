from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

class Project(models.Model):
    users = models.ManyToManyField(User, related_name='assigned_projects', blank=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    @property
    def progress(self):
        total = self.tasks.count()
        if total == 0:
            return 0
        completed = self.tasks.filter(completed=True).count()
        return round((completed / total) * 100, 2)

    def __str__(self):
        return self.name
    
class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.project.name})"


class Material(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='materials')
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=20)  # e.g., bags, kg, m³

    def __str__(self):
        return f"{self.name} for {self.project.name}"


class Labourer(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='labourers')
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)  # e.g., mason, carpenter, foreman
    contact = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name} ({self.role})"


class Report(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reports')
    date = models.DateField(auto_now_add=True)
    content = models.TextField()
    image = models.ImageField(upload_to='reports/', blank=True, null=True)

    def __str__(self):
        return f"Report for {self.project.name} on {self.date}"
    
class Profile(models.Model):
    ROLE_CHOICES = (
        ('manager', 'Site Manager'),
        ('worker', 'Site Worker'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='worker')

    def __str__(self):
        return f"{self.user.username} - {self.role}"

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

