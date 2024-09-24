from fastapi import WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"新しい接続が確立されました。現在の接続数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"接続が切断されました。現在の接続数: {len(self.active_connections)}")

    async def broadcast(self, message: bytes):
        print(f"ブロードキャスト: {len(self.active_connections)}個の接続にメッセージを送信します")
        for connection in self.active_connections:
            await connection.send_bytes(message)

manager = ConnectionManager()