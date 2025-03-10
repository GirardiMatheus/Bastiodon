import time
import psutil
from django.core.cache import cache
from django.db import connection

class MetricsCollector:
    
    @staticmethod
    def collect_system_metrics():

        metrics = {
            'cpu_usage': psutil.cpu_percent(interval=0.1),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
        }
        return metrics
    
    @staticmethod
    def collect_application_metrics():

        db_connected = False
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_connected = True
        except:
            pass
            
        redis_connected = False
        try:
            cache.set('health_check', 'ok', 1)
            redis_value = cache.get('health_check')
            redis_connected = (redis_value == 'ok')
        except:
            pass
            
        response_times = cache.get('response_times') or []
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        metrics = {
            'database_connected': db_connected,
            'redis_connected': redis_connected,
            'avg_response_time': avg_response_time,
            'total_requests': cache.get('total_requests') or 0,
            'error_count': cache.get('error_count') or 0,
        }
        return metrics
    
    @staticmethod
    def collect_service_metrics():

        from routing.service_registry import ServiceRegistry
        
        registry = ServiceRegistry()
        metrics = {}
        
        for service_name, service_config in registry.get_all_services().items():
            service_metrics = {
                'endpoints': len(service_config.get('endpoints', [])),
                'routes': len(service_config.get('routes', [])),
                'healthy_endpoints': 0,
            }
            
            from routing.resolver import ServiceResolver
            for endpoint in service_config.get('endpoints', []):
                if ServiceResolver.is_service_healthy(service_name, endpoint):
                    service_metrics['healthy_endpoints'] += 1
                    
            metrics[service_name] = service_metrics
            
        return metrics
    
    @classmethod
    def collect_all_metrics(cls):
        return {
            'system': cls.collect_system_metrics(),
            'application': cls.collect_application_metrics(),
            'services': cls.collect_service_metrics(),
            'timestamp': int(time.time()),
        }