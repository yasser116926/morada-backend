from django.db import models
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User


class Artwork(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    image = models.ImageField(upload_to='artworks/')

    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # ✅ NEW FIELDS
    size = models.CharField(max_length=100, blank=True)
    material = models.CharField(max_length=100, blank=True)

    CURRENCY_CHOICES = [
        ('USD', 'USD'),
        ('KSH', 'KSH'),
    ]
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')

    location = models.CharField(max_length=200, blank=True)

    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    image = models.ImageField(upload_to='events/', null=True, blank=True)

    location = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title        



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    receive_updates = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username   



from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    is_admin = models.BooleanField(default=False)

    receive_updates = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username            