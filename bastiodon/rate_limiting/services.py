import time
from django.core.cache import cache
from django.conf import settings
from rest_framework.exceptions import Throttled

class RateLimitService:

    
    @staticmethod
    def get_client_identifier(request):

        if hasattr(request, 'access_token'):
            return f"token:{request.access_token.token}"
        
        api_key = request.headers.get('X-API-Key')
        if api_key:
            return f"apikey:{api_key}"
        
        return f"ip:{request.META.get('REMOTE_ADDR', '0.0.0.0')}"
    
    @staticmethod
    def get_rate_limit(request):

        from authentication.models import ServiceClient
        
        api_key = request.headers.get('X-API-Key')
        if api_key:
            try:
                service = ServiceClient.objects.get(api_key=api_key, is_active=True)
                return service.rate_limit
            except ServiceClient.DoesNotExist:
                pass
                
        return getattr(settings, 'RATE_LIMITING', {}).get('DEFAULT_LIMIT', 100)
    
    @classmethod
    def check_rate_limit(cls, request):

        if not getattr(settings, 'RATE_LIMITING', {}).get('ENABLED', True):
            return True
            
        identifier = cls.get_client_identifier(request)
        limit = cls.get_rate_limit(request)
        
        prefix = getattr(settings, 'RATE_LIMITING', {}).get('CACHE_PREFIX', 'ratelimit')
        cache_key = f"{prefix}:{identifier}"
        
        period = 60
        
        pipe = cache.client.pipeline()
        pipe.get(cache_key)
        pipe.incr(cache_key)
        pipe.expire(cache_key, period)
        count, _, _ = pipe.execute()
        
        count = int(count or 0)
        
        if count > limit:
            ttl = cache.ttl(cache_key)
            if ttl < 0:
                ttl = period
                
            request.rate_limit_info = {
                'limit': limit,
                'remaining': max(0, limit - count),
                'reset': int(time.time()) + ttl
            }
            
            return False
            
        request.rate_limit_info = {
            'limit': limit,
            'remaining': max(0, limit - count),
            'reset': int(time.time()) + period
        }
        
        return True