import os as _os

_path = _os.path.dirname(__file__) + '\\bin;' + _os.environ['PATH']
_os.environ['PATH'] = _path
