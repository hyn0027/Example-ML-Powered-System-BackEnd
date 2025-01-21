from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio


class ProcessConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(json.dumps({"message": "WebSocket connection established"}))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.send(json.dumps({"message": "Processing started"}))

        # Simulate a long-running process
        for step in range(5):
            await asyncio.sleep(2)
            await self.send(json.dumps({"status": f"Step {step + 1} completed"}))

        await self.send(json.dumps({"message": "Processing complete"}))
