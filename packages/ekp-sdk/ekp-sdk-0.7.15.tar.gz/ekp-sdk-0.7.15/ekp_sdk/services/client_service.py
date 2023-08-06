import json
import logging
import time

import aiohttp_cors
import socketio
from aiohttp import web


class ClientService:
    def __init__(self, port, plugin_id):
        self.port = port
        self.plugin_id = plugin_id
        self.sio = self.__get_socket_io()
        self.app = self.__get_web_app()
        self.sio.attach(self.app)
        self.controllers = []

    def __get_socket_io(self):
        sio = socketio.AsyncServer(
            async_mode='aiohttp', cors_allowed_origins='*')

        @sio.event
        async def connect(sid, environ, auth):
            logging.info(f"✨ Client connected: {sid} => {len(self.controllers)} controllers")
            for controller in self.controllers:
                await controller.on_connect(sid)

        @sio.on('client-state-changed')
        async def on_client_state_changed(sid, data):
            logging.info(f"📣 Client state changed: {sid} => {len(self.controllers)} controllers")
            for controller in self.controllers:
                await controller.on_client_state_changed(sid, json.loads(data))

        return sio

    def __get_web_app(self):
        app = web.Application()

        cors = aiohttp_cors.setup(app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_methods="*",
                allow_headers="*",
            )
        })

        cors.add(app.router.add_static('/static', 'static'))

        return app

    def listen(self):
        web.run_app(self.app, port=self.port)

    def add_controller(self, controller):
        self.controllers.append(controller)

    async def emit_busy(self, sid, collection_name):
        logging.info(f"📣 Emit busy: {collection_name} => {sid}")
        
        layer = {
            "id": f"busy-{collection_name}",
            "collectionName": "busy",
            "set": [{"id": collection_name, }],
            "timestamp": int(time.time())
        }
        await self.emit_add_layers(sid, [layer])

    async def emit_done(self, sid, collection_name):
        logging.info(f"📣 Emit done: {collection_name} => {sid}")
        
        message = {
            "query": {
                "id": f'busy-{collection_name}',
            }
        }
        await self.sio.emit('remove-layers', json.dumps(message), room=sid)

    async def emit_menu(self, sid, icon, title, nav_link, aliases=None, short_link=None, order=None, id=None):
        """
        Sends menu layer from server to the client side
        """
        
        if not id:
            id = f"{self.plugin_id}_{nav_link}"

        logging.info(f"📣 Emit menu: {id} => {sid}")
            
        layer = {
            "id": id,
            "collectionName": "menus",
            "set": [
                {
                    "id": id,
                    "icon": icon,
                    "title": title,
                    "navLink": nav_link,
                    "aliases": aliases,
                    "shortLink": short_link,
                    "order": order
                }
            ],
            "timestamp": int(time.time())
        }

        await self.emit_add_layers(sid, [layer])

    async def emit_page(self, sid, path, element):
        """
        Sends main page content from server to the client side
        """

        logging.info(f"📣 Emit menu: {path} => {sid}")

        layer = {
            "id": f"{self.plugin_id}_page_{path}",
            "collectionName": "pages",
            "set": [
                {
                    "id": path,
                    "element": element
                }
            ],
            "timestamp": int(time.time())
        }

        await self.emit_add_layers(sid, [layer])

    async def emit_documents(self, sid, collection_name, documents, layer_id=None):

        logging.info(f"📣 Emit documents: {collection_name}({len(documents)}) => {sid}")
        
        if layer_id == None:
            layer_id = f"{self.plugin_id}_{collection_name}"
            
        layer = {
            "id": layer_id,
            "collectionName": collection_name,
            "set": documents,
            "timestamp": int(time.time())
        }

        await self.emit_add_layers(sid, [layer])

    async def emit_add_layers(self, sid, layers):
        message = {
            "layers": layers
        }

        await self.sio.emit('add-layers', json.dumps(message), room=sid)
