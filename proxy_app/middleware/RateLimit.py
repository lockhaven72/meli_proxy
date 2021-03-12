from proxy_app.models import UserSession
from django.http import HttpResponse
from django.utils import timezone
from proxy_app.classes.Metrics import Metrics
import os
import datetime

class RateLimit:
    def __init__(self, get_response):
        self.get_response = get_response
    

    def __call__(self, request):
        user_session = UserSession(ip_address=request.META.get('REMOTE_ADDR'), requested_endpoint=request.path, date=datetime.datetime.now(tz=timezone.get_current_timezone()).strftime("%Y-%m-%d %H:%M:%S"))
        try:
            if not self.check_user_session_entries(user_session):
                user_session.save()
                Metrics.concurrent_requests_gauge.inc()
        except Exception as err:
            Metrics.exceptions_counter.inc()
            return HttpResponse(content=repr(err), status=429)
        response = self.get_response(request)
        try:
           user_session.delete()
           Metrics.concurrent_requests_gauge.dec() 
        except Exception as err:
            Metrics.exceptions_counter.inc()
            return HttpResponse(content="An error was detected while deleting user session from database.", status=500)
        return response
    

    def check_user_session_entries(self, user_session):
        if len(UserSession.objects.filter(ip_address=user_session.ip_address)) > int(os.getenv('MAX_USER_REQUESTS', os.environ['MAX_USER_REQUESTS'])):
            raise Exception(f"Too many requests sent by the user {user_session.ip_address}, please retry later.") 
        elif len(UserSession.objects.filter(requested_endpoint=user_session.requested_endpoint)) > int(os.getenv('MAX_USER_REQUESTS', os.environ['MAX_USER_REQUESTS'])):
            raise Exception(f"Too many requests sent to the {user_session.requested_endpoint} endpoint, please retry later.") 
        elif len(UserSession.objects.filter(ip_address=user_session.ip_address, requested_endpoint=user_session.requested_endpoint)) > int(os.getenv('MAX_ENDPOINT_REQUESTS', os.environ['MAX_ENDPOINT_REQUESTS'])):
            raise Exception(f"Too many requests sent by the user {user_session.ip_address} to the {user_session.requested_endpoint} endpoint, please retry later.") 
        return