from django.http import HttpResponse
from .services import CacheService

class CacheMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        cached_response = CacheService.get_cached_response(request)
        
        if cached_response:
            response = HttpResponse(
                content=cached_response['content'],
                status=cached_response['status_code']
            )
            
            for header, value in cached_response['headers'].items():
                if header not in ('Content-Length',): 
                    response[header] = value
                    
            response['X-Cache'] = 'HIT'
            return response
            
        response = self.get_response(request)
        
        CacheService.cache_response(request, response)
        response['X-Cache'] = 'MISS'
        
        return response