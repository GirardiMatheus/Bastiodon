from django.http import JsonResponse
from routing.routes import RouteManager
from routing.proxy import ServiceProxy
from authentication.models import ServiceClient

class RoutingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        route_info = RouteManager.match_route(request)
        
        if route_info:
            if route_info['auth_required'] and not self._is_authenticated(request):
                return JsonResponse(
                    {'error': 'Authentication required'}, 
                    status=401
                )
                

            if 'rate_limit' in route_info and route_info['rate_limit']:
                from rate_limiting.services import RateLimitService
                
                original_get_rate_limit = RateLimitService.get_rate_limit
                

                def route_rate_limit(req):
                    return route_info['rate_limit']
                    
                RateLimitService.get_rate_limit = route_rate_limit
                
                if not RateLimitService.check_rate_limit(request):
                    RateLimitService.get_rate_limit = original_get_rate_limit
                    
                    return JsonResponse(
                        {'error': 'Rate limit exceeded'}, 
                        status=429
                    )
                
                RateLimitService.get_rate_limit = original_get_rate_limit
            
            return ServiceProxy.forward_request(request, route_info)
            

        return self.get_response(request)
        
    def _is_authenticated(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            return True
            
        api_key = request.headers.get('X-API-Key')
        if api_key:
            try:
                service = ServiceClient.objects.get(api_key=api_key, is_active=True)
                request.service_client = service
                return True
            except ServiceClient.DoesNotExist:
                pass
                
        return False