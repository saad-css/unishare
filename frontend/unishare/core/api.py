import requests
from .config import BASE_URL

TIMEOUT = 8


def post_json(endpoint: str, payload: dict):
    # Send a JSON request to the backend and return the raw response.
    return requests.post(f'{BASE_URL}{endpoint}', json=payload, timeout=TIMEOUT)


def get_json(endpoint: str):
    # Fetch JSON data from the backend and return the decoded response body.
    response = requests.get(f'{BASE_URL}{endpoint}', timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def upload_file(endpoint: str, file_path: str, form_data: dict):
    # Send a multipart upload request with the selected file and form fields.
    with open(file_path, 'rb') as file_obj:
        return requests.post(
            f'{BASE_URL}{endpoint}',
            files={'file': file_obj},
            data=form_data,
            timeout=20,
        )
