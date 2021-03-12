from django.http import HttpResponse
from proxy_app.classes.Metrics import Metrics

class TokenChecker:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Pre validation in request
        if request.path != '/metrics':
            try:
                self.check_bearer_token(request)
            except Exception:
                Metrics.exceptions_counter.inc()
                return HttpResponse(content="Bearer token not found in request.", status=400)
        response = self.get_response(request)
        # Post validation in view response
        return response

    def check_bearer_token(self, request):
        if 'Authorization' not in request.headers.keys() or 'Bearer' not in request.headers['Authorization']:
            raise Exception('NoBearerToken')
        return