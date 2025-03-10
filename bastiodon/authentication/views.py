from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from .models import ServiceClient, UserProfile, ServiceAccess
from .serializers import (
    UserSerializer,
    ServiceClientSerializer,
    ServiceAccessSerializer,
    UserProfileSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]

class ServiceClientViewSet(viewsets.ModelViewSet):
    queryset = ServiceClient.objects.all()
    serializer_class = ServiceClientSerializer
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    
    @action(detail=True, methods=['post'])
    def regenerate_key(self, request, pk=None):
        service = self.get_object()
        import uuid
        service.api_key = uuid.uuid4().hex
        service.save()
        return Response({'api_key': service.api_key})

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    
    @action(detail=True, methods=['post'])
    def update_service_access(self, request, pk=None):
        profile = self.get_object()
        service_id = request.data.get('service_id')
        can_access = request.data.get('can_access', True)
        
        try:
            service = ServiceClient.objects.get(id=service_id)
            access, created = ServiceAccess.objects.get_or_create(
                user_profile=profile,
                service=service,
                defaults={'can_access': can_access}
            )
            
            if not created:
                access.can_access = can_access
                access.save()
                
            return Response({'status': 'service access updated'})
        except ServiceClient.DoesNotExist:
            return Response(
                {'error': 'Service not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )