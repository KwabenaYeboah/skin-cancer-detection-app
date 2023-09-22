import cv2
import numpy as np

from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.views import View
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic.edit import FormView
from django.db.models.query import QuerySet
from django.views.generic import TemplateView

#API
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .butils import classify_image 
from .serializers import ImageUploadSerializer

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
        'f1_score': '91%',
        'val_precision': '90%',  
        'val_recall': '89%',  
        # 'test_loss': 0.31, 
        'test_accuracy': '90.7%',
        'auc_score':'97%'
    }
        return render(request, 'prediction/metrics.html', context)
    

class AboutView(TemplateView):
    template_name = "prediction/about.html"
    
    

# class ImageClassificationView(APIView):
#     parser_classes = (MultiPartParser,)
#     def post(self, request, *args, **kwargs):
#         serializer = ImageUploadSerializer(data=request.data)
#         if serializer.is_valid():
#             image = serializer.validated_data['image']
#             result, confidence = classify_image(image)

#             return Response({'result': result, 'confidence': confidence}, status=status.HTTP_200_OK)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ImageClassificationView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, *args, **kwargs):
        serializer = ImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            image_file = serializer.validated_data['image']
            
            image_data = image_file.read()
            nparr = np.fromstring(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is not None:
                result, confidence = classify_image(img)

                return Response({'result': result, 'confidence': confidence}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to decode image'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)