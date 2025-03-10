from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ServiceClient, UserProfile, ServiceAccess

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)

class ServiceClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceClient
        fields = ('id', 'name', 'api_key', 'is_active', 'rate_limit')
        read_only_fields = ('id', 'api_key')

class ServiceAccessSerializer(serializers.ModelSerializer):
    service_name = serializers.ReadOnlyField(source='service.name')
    
    class Meta:
        model = ServiceAccess
        fields = ('id', 'service', 'service_name', 'can_access')
        read_only_fields = ('id',)

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    service_access = ServiceAccessSerializer(source='serviceaccess_set', many=True, read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'service_access')
        read_only_fields = ('id',)