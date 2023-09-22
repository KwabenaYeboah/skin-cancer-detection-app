import cv2
from tensorflow.keras.models import load_model
import numpy as np
import os

from django.conf import settings

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# Load the model just once when the module is imported
model_path = os.path.join(settings.BASE_DIR, 'classifier/efficientnetb3.h5')
model = load_model(model_path)
Labels = ['Benign', 'Malignant']

def classify_image(img):
    img = cv2.resize(img, (224, 224))
    x = model.predict(np.asarray([img]))[0]
    print("X:",x)
    class_x = np.argmax(x)
    return Labels[class_x], x[class_x]*100