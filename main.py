import sys
from typing import Dict, List
from termcolor import colored
import yaml

from src.functions import do_step


global global_variables


if __name__ == '__main__':
    global_variables = {}
    yaml_dir = sys.argv[1]

    print('----------------')
    print(colored('Started...', 'green'))
    print(colored(f'Loading test from directory: {yaml_dir}', 'blue'))
    file = open(f'{yaml_dir}/steps.yaml', 'r').read()
    print(colored('Loaded file', 'green'))
    yaml_file = yaml.safe_load(file)
    print(colored('Serialized yaml file', 'green'))
    print('----------------')
    
    assert 'steps' in yaml_file
    assert 'url' in yaml_file
    steps: List[Dict] = yaml_file['steps']
    url: str = yaml_file['url']
    headers: dict = yaml_file.get('headers')

    failed_index = len(steps)
    for index, step in enumerate(steps): 
        if 'template' in step:
            template_file_name = step['template']
            template_file = open(f'{yaml_dir}/{template_file_name}', 'r').read()
            forward = yaml.safe_load(template_file)['forward']
        else:
            forward = step['forward']
        succeed = do_step(forward, url, headers, global_variables)
        if not succeed:
            failed_index = index
            print('Skipped other test')
            break
    
    print('\nRoll back\n----------------')
    
    for index, step in enumerate(reversed(steps)):
        if index < (len(steps) - failed_index) - 1:
            continue
        if 'template' in step:
            template_file_name = step['template']
            template_file = open(f'{yaml_dir}/{template_file_name}', 'r').read()
            try:
                rollback = yaml.safe_load(template_file)['rollback']
            except KeyError:
                continue
        else:
            try:
                rollback = step['rollback']
            except KeyError:
                continue
        do_step(rollback, url, headers, global_variables)
        
    print(
        'Finished with status:',
        colored('failed', 'red')
        if failed_index != len(steps)
        else colored('success', 'green')
    )
    print('')
    if failed_index != len(steps):
        sys.exit(0)
