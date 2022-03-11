import re
import sys
import requests

from src.helpers import helper_maps
from termcolor import colored

from time import perf_counter


REGEX_GLOBAL_VAR = r'^\$\(([A-Za-z0-9_]+)\)$'


def do_step(
        data: dict,
        url: str,
        headers: dict,
        global_variables: dict,
):
    name: str = data['name']
    endpoint: str = data['endpoint']
    method: str = data['method']
    assertions: [dict] = data.get('assertions')
    payload: dict = data.get('payload')
    endpoint_url = f'{url}{endpoint}'

    print(colored(f'>> {name}', 'yellow', attrs=['bold']))
    
    start_request_time = perf_counter()
    res = None
    if method.lower() == 'get':
        res = requests.get(endpoint_url, headers=headers)
    if method.lower() == 'post':
        res = post_request(endpoint_url, headers, payload, global_variables)
    if method.lower() == 'delete':
        res = requests.delete(endpoint_url, headers=headers)

    if res is None:
        print(f'Method "{method}" not supported.')

    elapsed_request_time = perf_counter() - start_request_time
    elapsed_request_time = "{:.2f}".format(elapsed_request_time)

    assertion_succeed, assertion_results = check_assertions(
        assertions=assertions,
        response=res
    )

    for msg in assertion_results:
        print(msg)
    if not assertion_succeed:
        print(
            'Responded failed message:',
            colored(res.content.decode(), 'magenta')
        )
    if data.get('store_response', False):
        store_response_to_global(
            data=data.get('store_response'),
            res_json=res.json(),
            global_var=global_variables
        )
    if data.get('debug_response', False):
        print(
            'Response:',
            colored(res.content.decode(), 'green')
        )
    print('Elapsed time:', f'{elapsed_request_time}s')
    print('----------------')

    return assertion_succeed


def post_request(url: str, headers: dict, payload: dict, global_variables: dict):
    yaml_dir = sys.argv[1]
    mode = 'json'
    file_keys = []
    files = []
    for key in payload.keys():
        field = payload[key]
        if isinstance(field, str) and re.match(REGEX_GLOBAL_VAR, field):
            payload[key] = get_value_from_global_var(field, global_variables)
        if not isinstance(field, dict):
            continue
        if field['type'].lower() == 'file':
            mode = 'multi-part'
            file = handle_file_field(yaml_dir, key, field)
            file_keys.append(key)
            files.append(file)
        elif field['type'].lower() == 'func':
            func_name = field['name']
            func_params = field['params']
            try:
                func = helper_maps[func_name]
            except KeyError:
                raise Exception(f'Unknown function {func_name}')
            payload[key] = func(**func_params)

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


def handle_file_field(yaml_dir: str, key: str, field: dict):
    filepath: str = f"{yaml_dir}/{field['path']}"
    mimetype: str = field['mimetype']
    filename: str = filepath.split('/')[-1]
    return key, (filename, open(filepath, 'rb'), mimetype)


def check_assertions(assertions: [dict], response):
    is_succeed = True
    results = []
    if not assertions:
        return is_succeed, results

    for assertion in assertions:
        http_status_code = assertion.get('httpStatusCode')
        if http_status_code is not None:
            succeed = response.status_code == http_status_code
            msg = 'Succeed' if succeed else 'Failed'
            msg = f'- {msg}: Expected status code {http_status_code},' \
                  f' got {response.status_code}'
            text_color = 'green' if succeed else 'red'
            msg = colored(msg, text_color)
            results.append(msg)
            is_succeed = succeed
            continue
    return is_succeed, results


def store_response_to_global(data: dict, res_json: dict, global_var: dict):
    for key in data.keys():
        var_id = data[key]['id']
        global_var[var_id] = res_json[key]
        print(f'Added "{var_id}" to global variables')


def get_value_from_global_var(key: str, global_var: dict):
    match = re.match(REGEX_GLOBAL_VAR, key)
    var_key = match.groups()[0]
    return global_var[var_key]
