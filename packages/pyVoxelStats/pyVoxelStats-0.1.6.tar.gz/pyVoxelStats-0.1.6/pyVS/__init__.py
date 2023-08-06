import os
import json

_ROOT = os.path.abspath(os.path.dirname(__file__))
def get_data(path):
    return os.path.join(_ROOT, 'data', path)

with open(os.path.dirname(__file__) + '/pkg_info.json') as fp:
    _info = json.load(fp)

__version__ = _info['version']
