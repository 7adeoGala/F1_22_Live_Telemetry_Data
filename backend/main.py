import asyncio
import json
import struct
from contextlib import asynccontextmanager
from typing import Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

# Configuración del servidor UDP
UDP_IP = "127.0.0.1"
UDP_PORT = 20777

# Decodificación de la estructura (Little Endian: <)
# F1 22 PacketHeader (Ajustado a 24 bytes para coincidir con la especificación y extraer correctamente los índices)
# H (2 bytes): packetFormat
# B (1 byte):  gameYear
# B (1 byte):  gameMajorVersion
# B (1 byte):  gameMinorVersion
# B (1 byte):  packetVersion
# B (1 byte):  packetId          -> Índice 5
# Q (8 bytes): sessionUID
# f (4 bytes): sessionTime       -> Índice 7
# I (4 bytes): frameIdentifier
# B (1 byte):  playerCarIndex
# B (1 byte):  secondaryPlayerCarIndex
HEADER_FORMAT = "<HBBBBBQfIBB"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        if not self.active_connections:
            return
        
        msg_str = json.dumps(message)
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_text(msg_str)
            except Exception:
                disconnected.add(connection)
                
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

class UDPListenerProtocol(asyncio.DatagramProtocol):
    def datagram_received(self, data: bytes, addr):
        # Desempaquetado seguro: verificamos que el tamaño mínimo del paquete se cumpla
        if len(data) >= HEADER_SIZE:
            try:
                # Extraemos los primeros 24 bytes correspondientes al Header
                unpacked_data = struct.unpack(HEADER_FORMAT, data[:HEADER_SIZE])
                
                payload = {
                    "packetId": unpacked_data[5],     # uint8 m_packetId
                    "sessionTime": unpacked_data[7]   # float m_sessionTime
                }
                
                # Emitimos el evento de forma no bloqueante a los clientes WebSocket
                asyncio.create_task(manager.broadcast(payload))
                
            except struct.error:
                pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_running_loop()
    # Inicialización del servidor UDP en un endpoint asíncrono y no bloqueante
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPListenerProtocol(),
        local_addr=(UDP_IP, UDP_PORT)
    )
    yield
    # Limpieza de recursos al apagar el servidor
    transport.close()

app = FastAPI(lifespan=lifespan)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Loop infinito para mantener la conexión WebSocket activa
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
