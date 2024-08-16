# myweb/consumers.py

import json
import socket
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            "notifications",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "notifications",
            self.channel_name
        )

    async def receive(self, text_data):
        ip_address = self.scope['client'][0]
        mac_address = self.get_mac_address(ip_address)
        message_data = {
            'message': text_data,
            'ip_address': ip_address,
            'mac_address': mac_address
        }
        await self.send(text_data=json.dumps(message_data))

    async def send_notification(self, event):
        message = event['message']
        ip_address = self.scope['client'][0]
        mac_address = self.get_mac_address(ip_address)
        await self.send(text_data=json.dumps({
            'message': message,
            'ip_address': ip_address,
            'mac_address': mac_address
        }))

    def get_mac_address(self, ip):
        try:
            return ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)][::-1])
        except Exception as e:
            return "00:00:00:00:00:00"
