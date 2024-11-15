from django.db import models

class Email(models.Model):
    subject = models.CharField(max_length=255)
    sender = models.CharField(max_length=255)
    sent_date = models.DateTimeField()
    received_date = models.DateTimeField()
    body = models.TextField()
    attachments = models.JSONField(default=list)

class User(models.Model):
    email = models.ForeignKey(Email, on_delete=models.CASCADE)
    login = models.CharField(max_length=255)
    password = models.CharField(max_length=255)