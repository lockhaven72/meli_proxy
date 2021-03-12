from django.shortcuts import render
from django.http import HttpResponse
from dotenv import load_dotenv
import requests
import os
load_dotenv()
# Create your views here.

dispatcher = {
    'GET': requests.get,
    'POST': requests.post,
    'PUT': requests.put,
    'DELETE': requests.delete,
    'OPTIONS': requests.options,
}

def proxy(request):
    redirect_url = os.getenv('MERCADOLIBRE_API', os.environ['MERCADOLIBRE_API'])+request.get_full_path()
    try:
        bearer_token = request.headers['Authorization']
        response = dispatcher[request.method](url=redirect_url, headers={'Authorization':f'{bearer_token}', 'Content-Type': 'application/json'})
        return HttpResponse(response)
    except Exception as e:
        print(e)
