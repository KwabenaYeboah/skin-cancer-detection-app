from django.urls import path
from .views import (PredictView, ResultView, 
                    HistoryView, UserHistoryPDFView, 
                    UserHistoryPDFEmailView, ModelPerformanceView,
                    AboutView)

urlpatterns = [
    path('', PredictView.as_view(), name='predict'),
    path('result/<uuid:pk>/', ResultView.as_view(), name='result'),
    path('history/', HistoryView.as_view(), name='history'),
    path('history/pdf/', UserHistoryPDFView.as_view(), name='user_history_pdf'),
    path('email-pdf/', UserHistoryPDFEmailView.as_view(), name='email_history'),
    path('model/metrics/', ModelPerformanceView.as_view(), name='metrics'),
    path('about/', AboutView.as_view(), name='about'),
]