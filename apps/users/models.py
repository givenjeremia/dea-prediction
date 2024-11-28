from django.db import models
from django.contrib.auth.models import User

import uuid

# Create your models here.
class Profile(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.user.first_name

