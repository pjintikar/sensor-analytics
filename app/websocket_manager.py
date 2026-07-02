from fastapi import WebSocket
import json

class ConnectionManager:
    """
    Keeps track of all connected WebSocket clients (like frontend dashboards).
    When an anomaly triggers, we blast a real-time message out to all of them.
    """

    def __init__(self):
        # 1. Initialize an empty list to track active browser connections
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        # 2. Handshake step: Accept the incoming connection request
        await websocket.accept()
        # 3. Save the connection handle into our list
        self.active_connections.append(websocket)
        print(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        # 4. Clean up closed connections to avoid memory leaks
        self.active_connections.remove(websocket)
        print(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast_alert(self, alert_data: dict):
        """Send an anomaly alert payload to every single connected client instantly"""
        # 5. Convert Python dictionary data into raw JSON text
        message = json.dumps(alert_data)
        
        # 6. Iterate through a safety copy of the active connections list
        for connection in self.active_connections.copy():
            try:
                # 7. Shoot the text down the open WebSocket pipeline
                await connection.send_text(message)
            except Exception:
                # 8. If a connection is quietly broken, remove it safely
                self.active_connections.remove(connection)

# Single shared instance used across the entire backend app
manager = ConnectionManager()