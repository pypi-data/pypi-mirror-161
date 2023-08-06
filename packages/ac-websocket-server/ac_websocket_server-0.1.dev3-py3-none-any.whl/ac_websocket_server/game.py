'''Assetto Corsa Game Server Class'''

import asyncio
from datetime import datetime
from genericpath import isdir
import logging
import os
import sys
import websockets

from ac_websocket_server.error import AssettoCorsaWebSocketError


class AssettoCorsaGameServer:
    '''Represents an Assetto Corsa Server.'''

    def __init__(self,  dummy: bool = False, game_directory: str = None) -> None:

        self.logger = logging.getLogger('ac-ws.game-server')

        self.game_directory = game_directory

        if sys.platform == 'linux':
            self.game_executable = f'{game_directory}/acServer'
        else:
            self.game_executable = f'{game_directory}/acServer.exe'

        if dummy:
            self.game_executable = 'ac_websocket_server/dummy.py'
            self.cwd = None
        else:
            self.cwd = self.game_directory

        self.process: asyncio.subprocess.Process = None

    async def start(self):
        '''Start the game server'''

        timestamp = datetime.now().strftime("%Y%M%d_%H%M%S")

        self.logger.info(f'Starting game server')

        os.makedirs(f'{self.game_directory}/logs/session', exist_ok=True)
        os.makedirs(f'{self.game_directory}/logs/error', exist_ok=True)

        session_file = open(
            f'{self.game_directory}/logs/session/output{timestamp}.log', 'w')
        error_file = open(
            f'{self.game_directory}/logs/error/error{timestamp}.log', 'w')

        try:
            self.process = await asyncio.create_subprocess_exec(
                self.game_executable, cwd=self.cwd,
                stdout=session_file, stderr=error_file)

            self.logger.info(f'Process pid is: {self.process.pid}')
        except PermissionError as e:
            self.logger.error(f'Process did not start: {e}')
            raise AssettoCorsaWebSocketError(e)

    async def stop(self):
        '''Stop the game server'''

        self.logger.info(f'Stopping game server')

        self.process.terminate()

        status_code = await asyncio.wait_for(self.process.wait(), None)
        self.logger.info(f'Game server exited with {status_code}')
