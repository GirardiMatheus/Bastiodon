import hashlib
import json
from django.core.cache import cache
from django.conf import settings

class CacheService:

    
    @staticmethod
    def get_cache_key(request):

        path = request.path
        method = request.method
        query_string = request.META.get('QUERY_STRING', '')
        
        body = ''
        if method in ['POST', 'PUT', 'PATCH'] and request.body:
            try:
                body = json.dumps(json.loads(request.body), sort_keys=True)
            except (ValueError, TypeError):
                body = request.body.decode('utf-8', errors='ignore')
        
        user_id = getattr(request.user, 'id', 'anonymous')
        
        key_data = f"{path}:{method}:{query_string}:{body}:{user_id}"
        return f"cache:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    @staticmethod
    def should_cache_request(request):

        if request.method != 'GET':
            return False
            
        if 'HTTP_CACHE_CONTROL' in request.META:
            if 'no-cache' in request.META['HTTP_CACHE_CONTROL'].lower():
                return False
                

        no_cache_paths = getattr(settings, 'CACHE_SETTINGS', {}).get('NO_CACHE_PATHS', [])
        for path in no_cache_paths:
            if request.path.startswith(path):
                return False
                
        return True
    
    @staticmethod
    def get_cache_ttl(request):

        path_ttls = getattr(settings, 'CACHE_SETTINGS', {}).get('PATH_TTLS', {})
        
        for path_prefix, ttl in path_ttls.items():
            if request.path.startswith(path_prefix):
                return ttl
                

        return getattr(settings, 'CACHE_SETTINGS', {}).get('DEFAULT_TTL', 300) 
    
    @classmethod
    def get_cached_response(cls, request):

        if not cls.should_cache_request(request):
            return None
            
        cache_key = cls.get_cache_key(request)
        cached_data = cache.get(cache_key)
        
        return cached_data
    
    @classmethod
    def cache_response(cls, request, response):

        if not cls.should_cache_request(request):
            return
            
        if response.status_code >= 400:
            return
            
        cache_key = cls.get_cache_key(request)
        ttl = cls.get_cache_ttl(request)
        
        response_data = {
            'content': response.content.decode('utf-8'),
            'status_code': response.status_code,
            'headers': dict(response.headers.items()),
        }
        
        cache.set(cache_key, response_data, ttl)

