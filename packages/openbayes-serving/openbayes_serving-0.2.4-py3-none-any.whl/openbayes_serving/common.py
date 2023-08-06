# -*- coding: utf-8 -*-

# -- stdlib --
import os
import sys

# -- third party --
# -- own --

# -- code --
class ServingError(Exception):

    def __init__(self, message, status_code=400, payload={}):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.payload = {**payload, 'error': message}


def detect_env():
    if sys.platform == 'win32':
        return 'local'

    if os.environ.get('OPENBAYES_JOB_URL'):
        return 'gear'

    if os.environ.get('OPENBAYES_SERVING_PRODUCTION'):
        return 'production'

    return 'local'
