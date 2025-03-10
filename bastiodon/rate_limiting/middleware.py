from django.http import JsonResponse
from .services import RateLimitService

class RateLimitMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._should_limit_request(request):
            if not RateLimitService.check_rate_limit(request):
                return self._build_throttled_response(request)
        
        response = self.get_response(request)
        
        if hasattr(request, 'rate_limit_info'):
            info = request.rate_limit_info
            response['X-RateLimit-Limit'] = str(info['limit'])
            response['X-RateLimit-Remaining'] = str(info['remaining'])
            response['X-RateLimit-Reset'] = str(info['reset'])
        
        return response
    
    def _should_limit_request(self, request):
        if request.path.startswith('/monitoring/health'):
            return False
            
        return True
    
    def _build_throttled_response(self, request):
        info = request.rate_limit_info
        response = JsonResponse({
            'detail': 'Request was throttled.',
            'availableIn': info['reset'] - int(time.time())
        }, status=429)
        
        response['X-RateLimit-Limit'] = str(info['limit'])
        response['X-RateLimit-Remaining'] = str(info['remaining'])
        response['X-RateLimit-Reset'] = str(info['reset'])
        
        return response