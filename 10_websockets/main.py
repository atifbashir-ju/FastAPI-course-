# 10 - WebSockets
# Topics: WebSocket connection, real-time chat, broadcast, rooms

from typing import Dict, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI(title="WebSockets - Real-time Chat")


# ─── Connection Manager ───────────────────────────────────────────────────────
class ConnectionManager:
    def __init__(self):
        # {room_name: [websocket1, websocket2, ...]}
        self.rooms: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: str, username: str):
        await websocket.accept()
        if room not in self.rooms:
            self.rooms[room] = []
        self.rooms[room].append(websocket)
        await self.broadcast(room, f"🟢 {username} room mein aaya", sender=None)

    def disconnect(self, websocket: WebSocket, room: str):
        if room in self.rooms:
            self.rooms[room].remove(websocket)

    async def send_personal(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, room: str, message: str, sender: WebSocket = None):
        """Room mein sabko message bhejo (sender ko chhod ke)"""
        if room in self.rooms:
            for connection in self.rooms[room]:
                if connection != sender:
                    await connection.send_text(message)

    async def broadcast_all(self, room: str, message: str):
        """Room mein sabko bhejo including sender"""
        if room in self.rooms:
            for connection in self.rooms[room]:
                await connection.send_text(message)

    def get_room_count(self, room: str) -> int:
        return len(self.rooms.get(room, []))


manager = ConnectionManager()


# ─── 1. Simple WebSocket ─────────────────────────────────────────────────────
@app.websocket("/ws/{client_id}")
async def websocket_simple(websocket: WebSocket, client_id: int):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Client {client_id} ne bheja: {data}")
    except WebSocketDisconnect:
        print(f"Client {client_id} disconnect ho gaya")


# ─── 2. Chat Room ─────────────────────────────────────────────────────────────
@app.websocket("/chat/{room}/{username}")
async def chat_room(websocket: WebSocket, room: str, username: str):
    await manager.connect(websocket, room, username)
    try:
        while True:
            message = await websocket.receive_text()
            # Sabko bhejo
            await manager.broadcast_all(room, f"{username}: {message}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
        await manager.broadcast(
            room, f"🔴 {username} room se chala gaya ({manager.get_room_count(room)} bache)"
        )


# ─── 3. REST + WebSocket combo ────────────────────────────────────────────────
@app.get("/rooms/{room}/users")
def get_room_users(room: str):
    return {
        "room": room,
        "connected_users": manager.get_room_count(room),
    }


# ─── 4. Test HTML Page (browser mein open karo) ──────────────────────────────
@app.get("/test-chat")
def chat_test_page():
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head><title>FastAPI WebSocket Chat Test</title></head>
<body style="font-family: sans-serif; max-width: 500px; margin: 40px auto;">
    <h2>WebSocket Chat Test</h2>
    <input id="room" placeholder="Room name" value="general" style="padding:6px; margin:4px">
    <input id="username" placeholder="Aapka naam" value="User1" style="padding:6px; margin:4px">
    <button onclick="connect()" style="padding:6px 12px">Connect</button>
    <br><br>
    <div id="messages" style="height:200px; border:1px solid #ccc; overflow-y:auto; padding:10px; margin-bottom:10px"></div>
    <input id="msg" placeholder="Message likho..." style="padding:6px; width:70%">
    <button onclick="sendMsg()" style="padding:6px 12px">Send</button>

    <script>
        let ws;
        function connect() {
            const room = document.getElementById("room").value;
            const user = document.getElementById("username").value;
            ws = new WebSocket(`ws://localhost:8000/chat/${room}/${user}`);
            ws.onmessage = (e) => {
                const div = document.getElementById("messages");
                div.innerHTML += `<p style="margin:4px 0">${e.data}</p>`;
                div.scrollTop = div.scrollHeight;
            };
            ws.onopen = () => addMsg("✅ Connected!");
            ws.onclose = () => addMsg("❌ Disconnected");
        }
        function sendMsg() {
            const msg = document.getElementById("msg").value;
            if (ws && msg) { ws.send(msg); document.getElementById("msg").value = ""; }
        }
        function addMsg(text) {
            document.getElementById("messages").innerHTML += `<p style="color:gray;margin:4px 0"><i>${text}</i></p>`;
        }
        document.getElementById("msg").addEventListener("keypress", (e) => { if(e.key === "Enter") sendMsg(); });
    </script>
</body>
</html>
""")
