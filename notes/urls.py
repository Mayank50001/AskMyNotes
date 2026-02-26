from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('api/subjects/', views.SubjectListCreateView.as_view(), name='api-subjects'),
    path('api/subjects/<str:name>/', views.SubjectDetailView.as_view(), name='api-subject-detail'),
    path('api/upload/', views.UploadPDFView.as_view(), name='api-upload'),
    path('api/ask/', views.AskView.as_view(), name='api-ask'),
    path('api/study/', views.StudyView.as_view(), name='api-study'),

    # Template views
    path('', views.home_view, name='home'),
    path('chat/', views.chat_view, name='chat'),
    path('study/', views.study_view, name='study'),
]
