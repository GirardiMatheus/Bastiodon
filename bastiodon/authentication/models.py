from django.db import models
from django.contrib.auth.models import User

class ServiceClient(models.Model):
    name = models.CharField(max_length=100)
    api_key = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    rate_limit = models.IntegerField(default=100)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    service_access = models.ManyToManyField(ServiceClient, through='ServiceAccess')

    def __str__(self):
        return self.user.username

class ServiceAccess(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    service = models.ForeignKey(ServiceClient, on_delete=models.CASCADE)
    can_access = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('user_profile', 'service')