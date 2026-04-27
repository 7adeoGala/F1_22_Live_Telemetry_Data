import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const WS_URL = 'ws://localhost:8000/ws';

export default function App() {
  const [connectionStatus, setConnectionStatus] = useState('CONNECTING');

  // Referencias para manipulación directa del DOM (Alto rendimiento a 60Hz)
  const packetIdRef = useRef(null);
  const sessionTimeRef = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => {
    let reconnectTimeout;

    const connectWebSocket = () => {
      setConnectionStatus('CONNECTING');
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnectionStatus('CONNECTED');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          // Actualización directa del DOM: O(1) y 0 re-renders en React
          // Ideal para los 60Hz de la telemetría del F1 22
          if (packetIdRef.current && data.packetId !== undefined) {
            packetIdRef.current.textContent = data.packetId;
          }
          if (sessionTimeRef.current && data.sessionTime !== undefined) {
            sessionTimeRef.current.textContent = Number(data.sessionTime).toFixed(3);
          }
        } catch (error) {
          console.error('Error parsing telemetry payload:', error);
        }
      };

      ws.onclose = () => {
        setConnectionStatus('DISCONNECTED');
        // Intento de reconexión automática tras 3 segundos
        reconnectTimeout = setTimeout(connectWebSocket, 3000);
      };

      ws.onerror = () => {
        ws.close(); // Forzamos el onclose para gestionar la reconexión
      };
    };

    connectWebSocket();

    // Cleanup: Cierra la conexión y limpia timeouts al desmontar el componente
    return () => {
      clearTimeout(reconnectTimeout);
      if (wsRef.current) {
        wsRef.current.onclose = null;
        wsRef.current.close();
      }
    };
  }, []);

  return (
    <div className="app-container">
      <h1>F1 22 Pitwall Dashboard</h1>
      <div className={`status-indicator ${connectionStatus.toLowerCase()}`}>
        Status: {connectionStatus}
      </div>

      <div className="telemetry-data">
        <div className="data-box">
          <h3>Packet ID</h3>
          <div className="value" ref={packetIdRef}>--</div>
        </div>
        <div className="data-box">
          <h3>Session Time</h3>
          <div className="value" ref={sessionTimeRef}>--</div>
        </div>
      </div>
    </div>
  );
}