#!/usr/bin/env python3

'''Dummy Game Server for development'''

import sys
import time

print('Dummy Game Server starting')
i = 0
try:
    while True:
        if i % 30 == 0:
            print(
                f'Dummy Server - Session timestamp {i} seconds')
        if i % 30 == 0:
            print(
                f'Dummy Server - Error timestamp {i} seconds', file=sys.stderr)
        time.sleep(1)
        i += 1
except KeyboardInterrupt:
    print('Dummy Game Server interrupted!')
