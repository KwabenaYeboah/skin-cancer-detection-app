from django.db import models
from django.contrib.auth.models import AbstractUser
import string
import random

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    verification_code_expires = models.DateTimeField(blank=True, null=True)
    
    def generate_verification_code(self):
        chars = string.digits
        return ''.join(random.choices(chars, k=6))
    
    def __str__(self):
        return self.email