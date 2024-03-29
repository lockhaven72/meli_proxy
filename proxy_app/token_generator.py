import requests
import os
from dotenv import load_dotenv
load_dotenv()

def generate auth_code():
    auth_url = f"https://auth.mercadolibre.com.ar/authorization?response_type=code&client_id={os.getenv('APP_ID')}&redirect_uri={os.getenv('REDIRECT_URL')}"
    print(auth_url)
    #response = requests.get(url=auth_url, allow_redirects=True).history

def generate_token(server_generated_authorization_code):
    token_generator_url = "https://api.mercadolibre.com/oauth/token"
    headers = {
        'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded'
    }
    payload = {
        'grant_type': 'authorization_code',
        'client_id': os.getenv('APP_ID'),
        'client_secret': os.getenv('SECRET_KEY'),
        'code': server_generated_authorization_code,
        'redirect_uri': os.getenv('REDIRECT_URL')
    }
    response = requests.post(url=token_generator_url, data=payload).json()
    bearer_token = response['access_token']
    print(bearer_token)