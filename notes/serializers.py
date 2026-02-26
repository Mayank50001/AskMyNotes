from rest_framework import serializers
from .models import Subject, Document


class SubjectSerializer(serializers.ModelSerializer):
    document_count = serializers.IntegerField(source='documents.count', read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'name', 'created_at', 'document_count']


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'subject', 'file', 'original_name', 'uploaded_at']


class AskRequestSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=50)
    question = serializers.CharField(max_length=1000)


class StudyRequestSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=50)
