from django.conf import settings
import re
from .service_registry import ServiceRegistry

class RouteManager:

    @staticmethod
    def get_route_patterns():

        registry = ServiceRegistry()
        routes = []
        
        for service_name, service_config in registry.get_all_services().items():
            for route in service_config.get('routes', []):
                routes.append({
                    'pattern': re.compile(route['path']),
                    'service': service_name,
                    'strip_prefix': route.get('strip_prefix', True),
                    'target_path': route.get('target_path', ''),
                    'methods': route.get('methods', ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']),
                    'rate_limit': route.get('rate_limit'),
                    'auth_required': route.get('auth_required', True),
                })
        
        return routes
    
    @classmethod
    def match_route(cls, request):

        path = request.path
        method = request.method
        
        for route in cls.get_route_patterns():
            match = route['pattern'].match(path)
            if match and method in route['methods']:
                if route['strip_prefix'] and route['target_path']:
                    groups = match.groups()
                    target_path = route['target_path']
                    for i, group in enumerate(groups, 1):
                        target_path = target_path.replace(f'${i}', group or '')
                    destination_path = target_path
                else:
                    destination_path = path
                
                return {
                    'service': route['service'],
                    'destination_path': destination_path,
                    'rate_limit': route['rate_limit'],
                    'auth_required': route['auth_required'],
                    'match': match
                }
        
        return None