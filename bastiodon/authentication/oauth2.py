from oauth2_provider.oauth2_validators import OAuth2Validator
from oauth2_provider.models import AccessToken
from datetime import datetime, timedelta
from django.utils import timezone

class CustomOAuth2Validator(OAuth2Validator):
    def validate_bearer_token(self, token, scopes, request):
        
        try:
            access_token = AccessToken.objects.get(token=token)
            if access_token.expires < timezone.now():
                return False
            
            token_scopes = access_token.scope.split()
            for scope in scopes:
                if scope not in token_scopes:
                    return False
                    
            request.user = access_token.user
            request.client = access_token.application
            request.scopes = scopes
            
            
            request.access_token = access_token
            
            return True
        except AccessToken.DoesNotExist:
            return False