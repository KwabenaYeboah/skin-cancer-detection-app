import cv2
import tensorflow as tf
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
trained_model_path = os.path.join(settings.BASE_DIR, 'classifier/efficientnetb3.h5')
trained_model = load_model(trained_model_path)
Labels = ['Benign', 'Malignant']

# Prefilter autoencoder model
path1 = os.path.join(settings.BASE_DIR, 'autoencoder/autoencoder.json')
json_file = open(path1, "r")
loaded_model_json = json_file.read()
json_file.close()
autoencoder = tf.keras.models.model_from_json(loaded_model_json)
path2 = os.path.join(settings.BASE_DIR, 'autoencoder/autoencoder.h5')
autoencoder.load_weights(path2)


THRESHOLD = 0.04

def predict_image(filename):
    img = cv2.imread(os.path.join(settings.MEDIA_ROOT, filename))
    img2 = cv2.resize(img, (224, 224))
    img = np.array(img2)
    img = img / 255.0
    img = np.reshape(img, (1, 224, 224, 3))

    decoded_img = autoencoder.predict(img)
    mse = np.mean((img - decoded_img) ** 2)
    print("MSE:", mse)
    if mse > THRESHOLD:
        return "Outlier", 0.0

    x = trained_model.predict(np.asarray([img2]))[0]
    print("X:",x)
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