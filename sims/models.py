from django.db import models
from django.contrib.auth.models import User

class ExampleModel(models.Model):
     name = models.CharField(max_length=100)
     created_at = models.DateTimeField(auto_now_add=True)
class Plan(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    attachment = models.FileField(upload_to='attachments/', blank=True, null=True)
    date_submitted = models.DateTimeField(auto_now_add=True)
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class PatientRecord(models.Model):
    name = models.CharField(max_length=100)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10)
