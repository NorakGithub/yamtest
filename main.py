from ast import Str
import json
from typing import Dict, List

import requests
import yaml

from src.functions import do_step

if __name__ == '__main__':
    print('----------------')
    print('Test beginned...')
    file = open('tests/steps.yaml', 'r').read()
    print('Loaded file')
    yaml_file = yaml.safe_load(file)
    print('Serialized yaml file')
    print('----------------')
    
    assert 'steps' in yaml_file
    assert 'url' in yaml_file
    steps: List[Dict] = yaml_file['steps']
    url: List[Str] = yaml_file['url']
    headers: dict = yaml_file['headers']

    for index, step in enumerate(steps):
        do_step(step['forward'], index, url, headers)
    
    print('Rolling back')
    print('----------------')
    
    for index, step in enumerate(reversed(steps)):
        do_step(step['rollback'], index, url, headers, 'rollback')
        
    print('Completed 🎉')
    print('')
