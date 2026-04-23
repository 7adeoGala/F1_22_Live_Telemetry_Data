# F1 22 Live Telemetry Dashboard

## 1. Finalidad del Proyecto
El objetivo de este proyecto es desarrollar una herramienta de visualización de datos de telemetría, en tiempo real, del videojuego F1 22 mediante la lectura e interpretación de paquetes UDP, con información vital de la sesión de juego.

Este proyecto sirve como base para el desarrollo de sistemas de ingesta de datos de alta frecuencia y visualización dinámica.

## 2. Arquitectura del Sistema
El sistema sigue un modelo de arquitectura desacoplada para garantizar baja latencia en la visualización:

* **Capa de Ingesta (Backend):** Un servicio en Python que actúa como servidor UDP "listener". Se encarga de recibir los datagramas binarios del juego, decodificar las estructuras en formato *Little Endian* (conforme a la v16 de F1 22) y transformar los datos brutos en objetos estructurados (JSON).
* **Capa de Comunicación:** Los datos procesados se transmiten del backend al frontend mediante **WebSockets**, permitiendo una actualización "push" inmediata sin necesidad de peticiones HTTP constantes.
* **Capa de Visualización (Frontend):** Una interfaz web reactiva que renderiza indicadores dinámicos (Dashboard) utilizando componentes gráficos optimizados.

## 3. Tecnologías Propuestas
* **Lenguaje Principal:** Python 3.10+
* **Librerías de Ingesta:** `socket` (para red) y `struct` o `ctypes` (para parsing de bytes).
* **Servidor de Aplicación:** `FastAPI` o `Flask-SocketIO`.
* **Frontend:** `React.js` o `Vue.js` (con librerías de gráficos).
* **Control de Versiones:** Git.

## 4. Estructura del Repositorio

```text
/f1-pitwall-dashboard
├── /backend                # Lógica de captura y procesamiento UDP
│   ├── core/               # Parsers de los paquetes de F1 22
│   ├── services/           # Servidor WebSocket y gestión de eventos
│   └── main.py             # Punto de entrada del backend
├── /frontend               # Interfaz de usuario (Dashboard)
│   ├── src/                # Componentes y lógica de visualización
│   └── public/
├── /docs                   # Especificaciones de paquetes y esquemas
└── README.md
```


