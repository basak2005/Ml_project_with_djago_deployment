from django.db import models

# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    address = models.TextField(blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)  # Fixed: CharField for phone numbers
    password = models.CharField(max_length=128)  # Increased for hashed passwords
    username = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.username