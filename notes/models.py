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

class ChatSession(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='sessions')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.subject.name})"


class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=[('user', 'User'), ('bot', 'Bot')])
    content = models.TextField()
    confidence = models.CharField(max_length=20, blank=True, null=True)
    citations = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role} in {self.session.name} - {self.created_at}"
