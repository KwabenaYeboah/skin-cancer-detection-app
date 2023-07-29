from django.contrib import admin
from .models import Predict

class PredictAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'uploaded_at', 'result', 'confidence')
    search_fields = ['user__username', 'result']
    list_filter = ('result', 'uploaded_at')
    date_hierarchy = 'uploaded_at'  

admin.site.register(Predict, PredictAdmin)
