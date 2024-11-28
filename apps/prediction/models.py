from django.db import models
import uuid

# Create your models here.
class DataModels(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 

    file = models.FileField(upload_to='model-keras/')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.user.first_name
