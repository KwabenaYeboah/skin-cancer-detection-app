from django.forms import ModelForm
from .models import Predict

class PredictForm(ModelForm):
    class Meta:
        model = Predict
        fields = ('image', 'note',)