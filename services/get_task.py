import httpx
import requests
BASE_URL = "https://shark-app-6wiyn.ondigitalocean.app/api/v1"
LOGIN_ENDPOINT = f"{BASE_URL}/auth/login"
TASK_ENDPOINT = f"{BASE_URL}/tasks/{{id}}"

LOGIN_PAYLOAD = {"email": "newAI@gmail.com", "password": "@test#123"}



def fetch_task_by_id(task_id: int) -> dict:
    """
    Logs in to get the token and fetches the task details by ID (Synchronous).
    """
    
    login_response = requests.post(LOGIN_ENDPOINT, json=LOGIN_PAYLOAD)
    if login_response.status_code != 201:
        raise ValueError(
            f"Login failed: {login_response.status_code} {login_response.text}"
        )

    token = login_response.json().get("token")
    if not token:
        raise ValueError("Token not found in login response.")

    
    headers = {"Authorization": f"Bearer {token}"}
    task_response = requests.get(TASK_ENDPOINT.format(id=task_id), headers=headers)
    if task_response.status_code != 200:
        raise ValueError(
            f"Failed to fetch task: {task_response.status_code} {task_response.text}"
        )

  
    return task_response.json()
