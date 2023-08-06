'''Assetto Corsa Websocket Server Class'''

import asyncio
import configparser
import hashlib
import logging
import os
import sys
from typing import Dict
import websockets

from ac_websocket_server.constants import HOST, PORT
from ac_websocket_server.error import AssettoCorsaWebSocketError
from ac_websocket_server.game import AssettoCorsaGameServer
from ac_websocket_server.handlers import handler


def check_acserver_file(game_directory: str = None) -> bool:

    if sys.platform == 'linux':
        file_name = f'{game_directory}/acServer'
        file_hash = 'f781ddfe02e68adfa170b28d0eccbbdc'
    else:
        file_name = f'{game_directory}/acServer.exe'
        file_hash = '357e1f1fd8451eac2d567e154f5ee537'

    try:
        with open(file_name, 'rb') as file_to_check:
            data = file_to_check.read()
            if file_hash != hashlib.md5(data).hexdigest():
                return False
    except FileNotFoundError:
        return False

    return True


def check_entry_list_file(game_directory: str = None) -> bool:

    return os.path.exists(f'{game_directory}/cfg/entry_list.ini')


def check_server_cfg_file(game_directory: str = None) -> bool:

    return os.path.exists(f'{game_directory}/cfg/server_cfg.ini')


def parse_server_cfg_file(game_directory: str = None) -> configparser.ConfigParser:

    config = configparser.ConfigParser()
    config.read(f'{game_directory}/cfg/server_cfg.ini')
    return config


class AssettoCorsaWebSocketServer:
    '''Represents an Assetto Corsa WebSocket Server.

    Allows control of an Assetto Corsa server with a websockets interface.'''

    def __init__(self,
                 host: str = HOST, port: int = PORT,
                 dummy: bool = False, game: str = None) -> None:

        self.logger = logging.getLogger('ac-ws.ws-server')

        self.host = host
        self.port = port

        self.dummy = dummy

        if not game:
            self.game_directory = os.getcwd()
        else:
            self.game_directory = game

        if not check_server_cfg_file(self.game_directory):
            raise AssettoCorsaWebSocketError(
                f'Missing server_cfg.ini file in {self.game_directory}')

        self.server_cfg = parse_server_cfg_file(self.game_directory)

        self.server_name = self.server_cfg['SERVER']['NAME']
        self.server_cars = self.server_cfg['SERVER']['CARS']
        self.server_udp_port = self.server_cfg['SERVER']['UDP_PORT']
        self.server_tcp_port = self.server_cfg['SERVER']['TCP_PORT']
        self.server_http_port = self.server_cfg['SERVER']['HTTP_PORT']

        if not check_entry_list_file(self.game_directory):
            raise AssettoCorsaWebSocketError(
                f'Missing entry_list.ini file in {self.game_directory}')

        if not check_acserver_file(self.game_directory):
            raise AssettoCorsaWebSocketError(
                f'Missing or mismatched acServer binary in {self.game_directory}')

        self.game_server = None

        self.send_queue = asyncio.Queue()

        self.stop_server: asyncio.Future = None

    async def consumer(self, message):
        if b'start_server' in message:
            self.logger.info('Received request to start game server')
            try:
                self.game = AssettoCorsaGameServer(
                    dummy=self.dummy,
                    game_directory=self.game_directory)
                await self.game.start()
                self.logger.info('Game server started')
            except AssettoCorsaWebSocketError as e:
                await self.send_queue.put(str(e))
            return
        if b'stop_server' in message:
            self.logger.info('Received request to stop game server')
            try:
                await self.game.stop()
                self.logger.info('Game server stopped')
            except AssettoCorsaWebSocketError as e:
                await self.send_queue.put(str(e))
            return

        response_message = f'Received unrecognised message: {message}'
        self.logger.debug(response_message)
        await self.send_queue.put(response_message)

    async def handler(self, websocket):

        await websocket.send(
            f'Welcome to the Assetto Corsa WebSocker server running at {self.host}:{self.port}')

        await websocket.send(f'Name: {self.server_name} Cars: {self.server_cars}, Ports: {self.server_udp_port} UDP, {self.server_tcp_port} TCP, {self.server_http_port} HTTP')

        await handler(websocket, self.consumer, self.producer)

    async def producer(self):
        data = await self.send_queue.get()
        return data

    async def start(self):
        '''Start the websocket server'''

        try:

            self.logger.info(f'Starting websocket server')

            self.stop_server = asyncio.Future()

            async with websockets.serve(self.handler, self.host, self.port):
                await self.stop_server

            self.logger.info(f'Stopping websocket server')

        except KeyboardInterrupt:
            self.logger.info(f'Interupting the server')

    async def stop(self):
        '''Stop the websocket server'''

        self.stop_server.set_result()
