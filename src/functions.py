from datetime import timedelta
import requests

from time import perf_counter


def do_step(data: dict, index: int, url: str, headers: dict, mode='forward'):
    name: str = data['name']
    endpoint: str = data['endpoint']
    method: str = data['method']
    expected_status: int = data['httpStatus']
    payload: dict = data['payload']
    result: str = '✅ Success'
    failed_reason: str = ''
    endpoint_url = f'{url}{endpoint}'

    print(f'> Step {mode} {index + 1}: {name}')
    
    start_request_time = perf_counter()
    if method.lower() == 'get':
        response = requests.get(endpoint_url, headers=headers)
    if method.lower() == 'post':
        response = requests.post(endpoint_url, headers=headers, json=payload)
    if method.lower() == 'delete':
        response = requests.delete(endpoint_url, headers=headers)
    elapsed_request_time = perf_counter() - start_request_time
    
    expected_status = response.status_code == expected_status
    result = '❌ failed' if not expected_status else result
    failed_reason = '' if expected_status else  f'Expected {expected_status} received {response.status_code} instead.'
    
    print(result, f'({elapsed_request_time} s)')
    if (failed_reason):
        print(failed_reason)
        print(f'Response: {response.json()}')
    print('----------------')
