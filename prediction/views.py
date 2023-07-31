from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.views import View
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic.edit import FormView
from django.db.models.query import QuerySet
from django.views.generic import TemplateView

from .models import Predict
from .forms import PredictForm
from .utils import (predict_image, generate_pdf_and_send_email, 
                    generate_user_history_pdf, generate_single_record_pdf_and_send_mail)

class PredictView(LoginRequiredMixin, FormView):
    template_name = 'prediction/predict.html'
    form_class = PredictForm

    def form_valid(self, form):
        image_instance = form.save(commit=False)
        image_instance.user = self.request.user
        image_instance.save()
        img_path = image_instance.image.name
        
        result, confidence = predict_image(img_path)

        image_instance.result = result
        image_instance.confidence = confidence
        image_instance.save()
    
        messages.success(self.request, 'Image uploaded and processed successfully')
        return redirect('result', image_instance.pk)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)
    
    
class ResultView(DetailView):
    model = Predict
    template_name = "prediction/result.html"
    context_object_name = 'prediction'
    
    
class HistoryView(LoginRequiredMixin, ListView):
    model = Predict
    template_name = 'prediction/history.html'
    context_object_name = 'predictions'
    paginate_by = 6
    
    def get_queryset(self) -> QuerySet[Any]:
        return Predict.objects.filter(user=self.request.user)



class UserHistoryPDFView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.uploads.count() < 1:
            messages.error(request, 'You have no records to download')
            return redirect('/')
        response = generate_user_history_pdf(request.user, request.build_absolute_uri())
        return response
    

class UserHistoryPDFEmailView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if request.user.uploads.count() < 1:
            messages.error(request, 'You have no records to download')
            return redirect('/')
        recipient_email = request.POST.get('recipient_email')
        message = request.POST.get('message')
        generate_pdf_and_send_email(request.user.pk, request.build_absolute_uri(), recipient_email, message)
        
        messages.success(request, 'Prediction history Successfully Sent. Check your email.')
        return redirect('history')
    
class EmailRecord(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        recipient_email = request.POST.get('recipient_email')
        message = request.POST.get('message')
        image_id = self.kwargs['pk']
        generate_single_record_pdf_and_send_mail(self.request.user.id, image_id, request.build_absolute_uri(), recipient_email, message)
        
        messages.success(request, 'Prediction result Successfully Sent. Check your email.')
        return redirect('result', image_id)

class ModelPerformanceView(View):
    def get(self, request):
        context = {
        'f1_score': 0.82,
        'val_precision': 0.83,  
        'val_recall': 0.82,  
        'test_loss': 0.31, 
        'test_accuracy': 0.84,
        'auc_score':0.89
    }
        return render(request, 'prediction/metrics.html', context)
    

class AboutView(TemplateView):
    template_name = "prediction/about.html"