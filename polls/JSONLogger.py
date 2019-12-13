import sys
import json
import logging
import time


class Handler(logging.Handler):
    def emit(self, record):
        if record.levelname == 'ERROR':
            fd = sys.stderr
        else:
            fd = sys.stdout

        print(json.dumps({
            'level': record.levelname.lower(),
            'ts': time.time(),
            'logger': record.name,
            'msg': record.getMessage(),
        }), file=fd)
