from django.conf import settings
import json
import os

class ServiceRegistry:

    _instance = None
    _services = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceRegistry, cls).__new__(cls)
            cls._instance._load_services()
        return cls._instance
    
    def _load_services(self):

        self._services = getattr(settings, 'MICROSERVICES', {})
        
        config_path = os.path.join(settings.BASE_DIR, 'config', 'services.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                try:
                    file_services = json.load(f)
                    for service_name, service_config in file_services.items():
                        if service_name not in self._services:
                            self._services[service_name] = service_config
                        else:
                            self._services[service_name].update(service_config)
                except json.JSONDecodeError:
                    pass
    
    def get_service(self, service_name):

        return self._services.get(service_name)
    
    def get_all_services(self):

        return self._services
    
    def register_service(self, service_name, service_config):

        self._services[service_name] = service_config
        
    def remove_service(self, service_name):

        if service_name in self._services:
            del self._services[service_name]