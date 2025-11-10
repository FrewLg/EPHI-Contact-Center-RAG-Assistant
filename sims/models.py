from django.db import models
from django.contrib.auth.models import User

import uuid

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

    #########
# class ChatSession(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     created = models.DateTimeField(auto_now_add=True)

#     @property
#     def messages(self):
#         return self.messages.all()

#     def __str__(self):
#         return str(self.id)


# class Message(models.Model):
#     session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
#     sender = models.CharField(max_length=10, choices=(('human', 'Human'), ('ai', 'AI')))
#     text = models.TextField()
#     created = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         preview = (self.text[:30] + '...') if len(self.text) > 30 else self.text
#         return f"{self.sender.capitalize()} @ {self.created.strftime('%Y-%m-%d %H:%M:%S')}:{preview}"