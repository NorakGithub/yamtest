from email import header
from fileinput import filename
import json
from operator import mod
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
        response = post_request(endpoint_url, headers, payload)
    if method.lower() == 'delete':
        response = requests.delete(endpoint_url, headers=headers)
    elapsed_request_time = perf_counter() - start_request_time
    elapsed_request_time = "{:.2f}".format(elapsed_request_time)
    
    expected_status = response.status_code == expected_status
    result = '❌ failed' if not expected_status else result
    failed_reason = (
      '' if expected_status 
      else f'Expected {expected_status} received {response.status_code} instead.'
    )
    
    print(result, f'({elapsed_request_time}s)')
    if (failed_reason):
        print(failed_reason)
        print(f'Response: {response.json()}')
    print('----------------')


def post_request(url: str, headers: dict, payload: dict):
    mode = 'json'
    file_keys = []
    files = []
    for key in payload.keys():
        if not isinstance(payload[key], dict):
            continue
        if payload[key]['type'].lower() != 'file':
            continue
        mode = 'multi-part'
        filepath: str = payload[key]['path']
        mimetype: str = payload[key]['mimetype']
        filename: str = filepath.split('/')[-1]
        file_keys.append(key)
        files.append(
          (key, (filename, open(filepath, 'rb'), mimetype))
        )
    for key in file_keys:
        payload.pop(key)
    
    if mode == 'multi-part':
        response = requests.post(
            url=url,
            headers=headers,
            data=payload,
            files=files,
        )
    else:
        response = requests.post(
            url=url,
            headers=headers,
            json=payload,
        )
    
    return response
