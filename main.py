import sys
from typing import Dict, List

import yaml

from src.functions import do_step

if __name__ == '__main__':
    yaml_dir = sys.argv[1]

    print('----------------')
    print('Test beginned...')
    print(f'Loading test from directory: {yaml_dir}')
    file = open(f'{yaml_dir}/steps.yaml', 'r').read()
    print('Loaded file')
    yaml_file = yaml.safe_load(file)
    print('Serialized yaml file')
    print('----------------')
    
    assert 'steps' in yaml_file
    assert 'url' in yaml_file
    steps: List[Dict] = yaml_file['steps']
    url: List[str] = yaml_file['url']
    headers: dict = yaml_file['headers']

    for index, step in enumerate(steps): 
        if 'template' in step:
            template_file_name = step['template']
            template_file = open(f'{yaml_dir}/{template_file_name}', 'r').read()
            forward = yaml.safe_load(template_file)['forward']
        else:
            forward = step['forward']
        do_step(forward, index, url, headers)
    
    print('Rolling back')
    print('----------------')
    
    for index, step in enumerate(reversed(steps)):
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
        do_step(rollback, index, url, headers, 'rollback')
        
    print('Completed 🎉')
    print('')
