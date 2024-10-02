import requests
from typing import Optional
from time import sleep


def send_request(url, method, data, json, attempt):
    try:
        if method == 'post':
            response = requests.post(url, data=data, json=json)
        elif method == 'get':
            response = requests.get(url)
        else:
            print("Method not implemented")
            return None
        if 200 <= response.status_code < 300:
            return response
        print(f"Attempt {attempt} failed: Unsuccessful status code {response.status_code}\n"
              f"Response JSON body: {response.json()}\n")
    except requests.RequestException as e:
        print(f"Attempt {attempt} failed: Request failed: {e}\n")
    return None


def send_request_with_retries(url, method='get', data=None, json=None, retries=6, delay=10) -> Optional[requests.Response]:
    print(f"Sending {method.upper()} request to {url}\n")
    for idx in range(retries):
        response = send_request(url, method, data, json, idx + 1)
        if response is not None:
            return response
        print(f"Retrying in {delay} seconds...\n")
        sleep(delay)
    print("Maximum number of retries exceeded\n")
    return None
