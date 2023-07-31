from __future__ import absolute_import, unicode_literals
from celery import shared_task

import cv2
import weasyprint
from tensorflow.keras.models import load_model
import numpy as np
import os

from django.conf import settings
from django.shortcuts import  get_list_or_404, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from django.http import FileResponse
from django.core.mail import EmailMessage
from io import BytesIO

from .models import Predict
from accounts.models import CustomUser


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# Load the model just once when the module is imported
trained_model_path = os.path.join(settings.BASE_DIR, 'best_epoch')
trained_model = load_model(trained_model_path)
Labels = ['Benign', 'Malignant']


def predict_image(filename):
    img = cv2.imread(os.path.join(settings.MEDIA_ROOT, filename))
    img = cv2.resize(img, (224, 224))
    img = img / 255
    x = trained_model.predict(np.asarray([img]))[0]
    class_x = np.argmax(x)
    return Labels[class_x], x[class_x]*100


def generate_user_history_pdf(user, base_url):
    predictions = get_list_or_404(Predict, user=user)
    html = render_to_string('prediction/history_pdf.html', {'predictions':predictions, 
                                                            'username':user.username, 
                                                            'email':user.email,
                                                            'timestamp':timezone.now()})
    
    pdf_file = BytesIO()
    weasyprint.HTML(string=html, base_url=base_url).write_pdf(pdf_file, stylesheets=[weasyprint.CSS(str(settings.STATIC_ROOT) + '/css/pdf.css')])
    pdf_file.seek(0)
    return FileResponse(pdf_file, content_type='application/pdf', as_attachment=True, filename=f'{user.username}_prediction_history.pdf')

def generate_single_history_pdf(img_id, base_url):
    prediction = get_object_or_404(Predict, pk=img_id)
    user = prediction.user
    html = render_to_string('prediction/single_history_pdf.html', {'prediction':prediction, 
                                                            'username':user.username, 
                                                            'email':user.email,
                                                            'timestamp':timezone.now()})
    
    pdf_file = BytesIO()
    weasyprint.HTML(string=html, base_url=base_url).write_pdf(pdf_file, stylesheets=[weasyprint.CSS(str(settings.STATIC_ROOT) + '/css/pdf.css')])
    pdf_file.seek(0)
    return FileResponse(pdf_file, content_type='application/pdf', as_attachment=True, filename=f'{user.username}_result.pdf')


def generate_pdf_and_send_email(user_id, base_url, recipient_email, message):
    user = get_object_or_404(CustomUser, pk=user_id)
    
    # Generate PDF
    pdf_file = generate_user_history_pdf(user, base_url)
    
    # Prepare and send email
    email = EmailMessage(
        'Your Prediction History',
        message,
        user.email,
        [recipient_email],
    )
    email.attach(f'{user.username}_prediction_history.pdf', pdf_file.getvalue(), 'application/pdf')
    email.send()
    
    

def generate_single_record_pdf_and_send_mail(user_id, img_id, base_url, recipient_email, message):
    pdf_file = generate_single_history_pdf(img_id, base_url)
    user = get_object_or_404(CustomUser, pk=user_id)
    # Prepare and send email
    email = EmailMessage(
        'Your Prediction Result',
        message,
        user.email,
        [recipient_email],
    )
    email.attach(f'{user.username}_result.pdf', pdf_file.getvalue(), 'application/pdf')
    email.send()