from django.db import models
from accounts.models import CustomUser
from django.core.exceptions import ValidationError
import uuid 

# Function to validate image size
def validate_image_size(image):
    file_size = image.file.size
    limit_mb = 10
    if file_size > limit_mb * 1024 * 1024:
        raise ValidationError(f"Maximum file size shouldn't exceed {limit_mb}MB")

class Predict(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='uploads')
    image = models.ImageField(upload_to='images/', validators=[validate_image_size])
    note = models.CharField(max_length=50, null=True, blank=True)
    result = models.CharField(max_length=20, null=True, blank=True)
    confidence = models.PositiveIntegerField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('-uploaded_at',)
        
    def __str__(self) -> str:
        return f"{self.image.name.split('/')[1]}"
