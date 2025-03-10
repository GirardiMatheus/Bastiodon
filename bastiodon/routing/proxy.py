import requests
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from .resolver import ServiceResolver
from .routes import RouteManager

class ServiceProxy:

    
    @staticmethod
    def forward_request(request, route_info):

        service_name = route_info['service']
        destination_path = route_info['destination_path']
        
        endpoint = ServiceResolver.get_healthy_endpoint(service_name)
        
        if not endpoint:
            return JsonResponse(
                {'error': f'Service {service_name} is not available'}, 
                status=503
            )
        
        url = f"{endpoint.rstrip('/')}/{destination_path.lstrip('/')}"
        
        headers = {
            'Content-Type': request.META.get('CONTENT_TYPE', 'application/json'),
            'Accept': request.META.get('HTTP_ACCEPT', '*/*'),
            'User-Agent': request.META.get('HTTP_USER_AGENT', 'BastiodonAPIGateway'),
            'X-Forwarded-For': request.META.get('REMOTE_ADDR', ''),
            'X-Original-URI': request.build_absolute_uri(),
            'X-Gateway-Service': 'Bastiodon'
        }
        
        if hasattr(request, 'user') and request.user.is_authenticated:
            headers['X-User-ID'] = str(request.user.id)
            headers['X-Username'] = request.user.username
        
        try:
            timeout = getattr(settings, 'SERVICE_REQUEST_TIMEOUT', 30)
            
            response = requests.request(
                method=request.method,
                url=url,
                headers=headers,
                data=request.body if request.method in ['POST', 'PUT', 'PATCH'] else None,
                params=request.GET.dict(),
                timeout=timeout,
                allow_redirects=False,  
            )
            
            django_response = HttpResponse(
                content=response.content,
                status=response.status_code,
            )
            
            for header, value in response.headers.items():
                if header.lower() not in ['content-length', 'connection', 'transfer-encoding']:
                    django_response[header] = value
            
            django_response['X-Served-By'] = f"{service_name}@{endpoint}"
            
            return django_response
            
        except requests.exceptions.Timeout:
            ServiceResolver.mark_endpoint_unhealthy(service_name, endpoint, 30)
            return JsonResponse(
                {'error': f'Service {service_name} timed out'}, 
                status=504
            )
        except requests.exceptions.ConnectionError:
            ServiceResolver.mark_endpoint_unhealthy(service_name, endpoint, 60)
            return JsonResponse(
                {'error': f'Service {service_name} is not reachable'}, 
                status=503
            )
        except Exception as e:
            return JsonResponse(
                {'error': f'Error forwarding request: {str(e)}'}, 
                status=500
            )