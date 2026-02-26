from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('api/subjects/', views.SubjectListCreateView.as_view(), name='api-subjects'),
    path('api/subjects/<str:name>/', views.SubjectDetailView.as_view(), name='api-subject-detail'),
    path('api/subjects/<int:pk>/delete/', views.SubjectDeleteView.as_view(), name='api-subject-delete'),
    
    path('api/upload/', views.UploadPDFView.as_view(), name='api-upload'),
    path('api/documents/<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='api-document-delete'),
    
    path('api/sessions/<int:pk>/delete/', views.ChatSessionDeleteView.as_view(), name='api-session-delete'),
    
    path('api/ask/', views.AskView.as_view(), name='api-ask'),
    path('api/study/', views.StudyView.as_view(), name='api-study'),

    # Template views
    path('', views.home_view, name='home'),
    path('chat/', views.chat_view, name='chat'),
    path('study/', views.study_view, name='study'),
]
