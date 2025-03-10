from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from .health_check import HealthCheck
from .metrics import MetricsCollector

@permission_classes([AllowAny])
class HealthCheckView(APIView):

    def get(self, request):
        health_data = HealthCheck.check_all()
        status_code = 200 if health_data['status'] == 'healthy' else 503
        return Response(health_data, status=status_code)

class MetricsView(APIView):

    def get(self, request):
        metrics = MetricsCollector.collect_all_metrics()
        return Response(metrics)