from django.db import models
#from django_prometheus.models import ExportModelOperationsMixin

# Create your models here.

class UserSession(models.Model):
    ip_address = models.CharField(max_length=15)
    requested_endpoint = models.CharField(max_length=100)
    date = models.DateTimeField()