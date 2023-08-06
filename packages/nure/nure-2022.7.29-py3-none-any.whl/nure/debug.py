import os
from distutils.util import strtobool

DEBUG = bool(strtobool(os.environ.get('DEBUG', 'false')))
