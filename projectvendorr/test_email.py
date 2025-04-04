# -*- coding: utf-8 -*-
import requests

# Get the token
login_data = {
    'email': 'raja.kmoorthy92@gmail.com',
    'password': 'Raja@1992'
}

try:
    # Get token
    token_response = requests.post('http://localhost:8000/api/token/', json=login_data)
    token_response.raise_for_status()  # Raise an exception for bad status codes
    token = token_response.json()['access_token']
    print("Successfully obtained token")

    # Send test email
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    email_data = {
        'subject': 'Test Email from Django Celery',
        'message': 'This is a test email sent via Celery task',
        'to_email': 'raja.kmoorthy92@gmail.com'
    }

    response = requests.post(
        'http://localhost:8000/api/test-email/',
        headers=headers,
        json=email_data
    )
    response.raise_for_status()
    print("Email task response:", response.json())

except requests.exceptions.RequestException as e:
    print("Error occurred:", str(e))
    if hasattr(e.response, 'text'):
        print("Response content:", e.response.text)
