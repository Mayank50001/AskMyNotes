from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import render
from .models import Subject, Document
from .serializers import SubjectSerializer, AskRequestSerializer, StudyRequestSerializer
from .services.embeddings import embed_texts
from .services.vectorstore import add_to_index
from .services.qa import process_pdf, ask_question
from .services.study import generate_study_material


class SubjectListCreateView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def get(self, request):
        subjects = Subject.objects.all()
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)

    def post(self, request):
        if Subject.objects.count() >= 3:
            return Response(
                {"error": "Maximum 3 subjects allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UploadPDFView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        subject_name = request.data.get('subject')
        pdf_file = request.FILES.get('file')

        if not subject_name or not pdf_file:
            return Response(
                {"error": "Both 'subject' and 'file' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            subject = Subject.objects.get(name=subject_name)
        except Subject.DoesNotExist:
            return Response(
                {"error": f"Subject '{subject_name}' not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        doc = Document.objects.create(
            subject=subject,
            file=pdf_file,
            original_name=pdf_file.name,
        )

        chunks = process_pdf(doc.file.path, pdf_file.name, subject_name)

        if chunks:
            try:
                texts = [c["text"] for c in chunks]
                embeddings = embed_texts(texts)
                add_to_index(subject_name, embeddings, chunks)
            except Exception as e:
                return Response(
                    {"error": f"Embedding failed: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(
            {"message": f"Uploaded and indexed {len(chunks)} chunks."},
            status=status.HTTP_201_CREATED,
        )


class AskView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AskRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        subject = serializer.validated_data['subject']
        question = serializer.validated_data['question']

        try:
            Subject.objects.get(name=subject)
        except Subject.DoesNotExist:
            return Response(
                {"error": f"Subject '{subject}' not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        result = ask_question(subject, question)
        return Response(result)


class StudyView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = StudyRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        subject = serializer.validated_data['subject']

        try:
            Subject.objects.get(name=subject)
        except Subject.DoesNotExist:
            return Response(
                {"error": f"Subject '{subject}' not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        result = generate_study_material(subject)
        return Response(result)


class SubjectDetailView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, name):
        try:
            subject = Subject.objects.get(name=name)
        except Subject.DoesNotExist:
            return Response(
                {"error": f"Subject '{name}' not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        docs = subject.documents.all().values('id', 'original_name', 'uploaded_at')
        return Response({
            "id": subject.id,
            "name": subject.name,
            "documents": list(docs),
        })


def home_view(request):
    subjects = Subject.objects.prefetch_related('documents').all()
    return render(request, 'notes/home.html', {'subjects': subjects})


def chat_view(request):
    subjects = Subject.objects.all()
    return render(request, 'notes/chat.html', {'subjects': subjects})


def study_view(request):
    subjects = Subject.objects.all()
    return render(request, 'notes/study.html', {'subjects': subjects})

