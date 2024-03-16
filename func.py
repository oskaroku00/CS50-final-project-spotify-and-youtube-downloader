import requests
import json

from main import session, API_BASE_URL


def api_json(url):
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    response = requests.get(API_BASE_URL + url, headers=headers).json()
    response = json.loads(json.dumps(response))

    return response

