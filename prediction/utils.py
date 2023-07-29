import cv2
import weasyprint
from tensorflow.keras.models import load_model
import numpy as np
import os

from django.conf import settings
from django.shortcuts import  get_list_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from django.http import FileResponse
from io import BytesIO

from .models import Predict


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# Load the model just once when the module is imported
trained_model_path = os.path.join(settings.BASE_DIR, 'best_epoch')
trained_model = load_model(trained_model_path)
Labels = ['Benign', 'Malignant']

def upload(filename):
    img = cv2.imread(os.path.join(settings.MEDIA_ROOT, filename))
    img = cv2.resize(img, (224, 224))
    img = img / 255
    x = trained_model.predict(np.asarray([img]))[0]
    class_x = np.argmax(x)
    print(x[class_x])
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
    