from django.db import models


class Subject(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Document(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='uploads/')
    original_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.original_name} ({self.subject.name})"
