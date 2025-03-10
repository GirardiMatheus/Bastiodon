from django.conf import settings
import random
from .service_registry import ServiceRegistry

class ServiceResolver:

    
    @staticmethod
    def resolve_service(service_name):

        registry = ServiceRegistry()
        service = registry.get_service(service_name)
        
        if not service:
            return None
            
        endpoints = service.get('endpoints', [])
        if not endpoints:
            return None
            
        strategy = service.get('load_balancing', 'random')
        
        if strategy == 'random':
            return random.choice(endpoints)
        elif strategy == 'round-robin':

            import time
            index = int(time.time()) % len(endpoints)
            return endpoints[index]
        elif strategy == 'least-connections':

            return random.choice(endpoints)
        else:
            return random.choice(endpoints)
    
    @staticmethod
    def is_service_healthy(service_name, endpoint):

        from django.core.cache import cache
        
        unhealthy_key = f"unhealthy:{service_name}:{endpoint}"
        return not cache.get(unhealthy_key)
    
    @classmethod
    def mark_endpoint_unhealthy(cls, service_name, endpoint, duration=60):

        from django.core.cache import cache
        
        unhealthy_key = f"unhealthy:{service_name}:{endpoint}"
        cache.set(unhealthy_key, True, duration)
        
    @classmethod
    def get_healthy_endpoint(cls, service_name):

        registry = ServiceRegistry()
        service = registry.get_service(service_name)
        
        if not service:
            return None
            
        endpoints = service.get('endpoints', [])
        
        healthy_endpoints = [
            endpoint for endpoint in endpoints
            if cls.is_service_healthy(service_name, endpoint)
        ]
        
        if not healthy_endpoints:

            return cls.resolve_service(service_name)
        

        strategy = service.get('load_balancing', 'random')
        
        if strategy == 'random' or strategy == 'least-connections':
            return random.choice(healthy_endpoints)
        elif strategy == 'round-robin':
            import time
            index = int(time.time()) % len(healthy_endpoints)
            return healthy_endpoints[index]
        else:
            return random.choice(healthy_endpoints)