'''Assetto Corsa Websocket Server'''

import logging
import sys


# logging.basicConfig()

# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s %(levelname)s %(message)s',
#                     filename='tmp/ac-ws.log',
#                     filemode='w')

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

logger = logging.getLogger('ac-ws')
