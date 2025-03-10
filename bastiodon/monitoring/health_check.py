import time
from django.db import connection
from django.core.cache import cache

class HealthCheck:
    
    @staticmethod
    def check_database():

        try:
            with connection.cursor() as cursor:
                start_time = time.time()
                cursor.execute("SELECT 1")
                duration = time.time() - start_time
                return {
                    'status': 'healthy',
                    'response_time': duration,
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
            }
    
    @staticmethod
    def check_cache():

        try:
            start_time = time.time()
            cache.set('health_check', 'ok', 1)
            value = cache.get('health_check')
            duration = time.time() - start_time
            
            if value == 'ok':
                return {
                    'status': 'healthy',
                    'response_time': duration,
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': 'Invalid cache value',
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
            }
    
    @staticmethod
    def check_services():

        from routing.service_registry import ServiceRegistry
        from routing.resolver import ServiceResolver
        
        registry = ServiceRegistry()
        service_health = {}
        
        for service_name, service_config in registry.get_all_services().items():
            endpoints = service_config.get('endpoints', [])
            healthy_endpoints = []
            
            for endpoint in endpoints:
                if ServiceResolver.is_service_healthy(service_name, endpoint):
                    healthy_endpoints.append(endpoint)
            
            service_health[service_name] = {
                'status': 'healthy' if healthy_endpoints else 'unhealthy',
                'healthy_endpoints': len(healthy_endpoints),
                'total_endpoints': len(endpoints),
            }
        
        return service_health
    
    @classmethod
    def check_all(cls):

        database = cls.check_database()
        cache_check = cls.check_cache()
        services = cls.check_services()
        
        overall_status = 'healthy'
        
        if database['status'] != 'healthy':
            overall_status = 'degraded'
            
        if cache_check['status'] != 'healthy':
            overall_status = 'degraded'
            
        for service_name, service_health in services.items():
            if service_health['status'] != 'healthy':
                if service_health['healthy_endpoints'] == 0:
                    overall_status = 'degraded'
        
        return {
            'status': overall_status,
            'timestamp': int(time.time()),
            'components': {
                'database': database,
                'cache': cache_check,
                'services': services,
            }
        }