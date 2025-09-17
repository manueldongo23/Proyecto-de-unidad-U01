🖥️ Simulador de Sistema Operativo – Unidad 01

Este proyecto implementa un simulador de un sistema operativo simple, que permite practicar los conceptos de:

Gestión de procesos (FCFS, SPN, Round Robin).

Planificación de CPU con métricas de desempeño.

Gestión de memoria (First-Fit y Best-Fit).

🚀 Requisitos

Python 3.10 o superior

Windows 10/11 (probado en ambos)

Entorno virtual (.venv) activado

📂 Estructura del proyecto
sim-unidad01/
│
├── src/              # Código fuente (sim_so.py)
├── config/           # Archivos JSON de configuración
├── docs/             # Informe técnico (PDF)
├── .gitignore
├── README.md         # Este archivo
└── GUIA_USUARIO.md   # Instrucciones detalladas

⚙️ Uso básico

Clonar o descargar el proyecto.

Activar el entorno virtual:

cd "$HOME\Desktop\sim-unidad01"
.\.venv\Scripts\Activate.ps1


Ejecutar el simulador con un archivo JSON:

python sim_so.py --config config\ejemplo_fcfs.json

🔄 Configuración rápida

Los parámetros se cambian editando un archivo JSON en config/.

CPU
"cpu": { "algoritmo": "FCFS" }


Opciones: "FCFS", "SPN", "RR".
Si usas "RR", añade "quantum": 4 (mínimo 2).

Procesos
"procesos": [
  { "pid": 1, "llegada": 0, "servicio": 12 },
  { "pid": 2, "llegada": 1, "servicio": 5 }
]

Memoria
"memoria": { "tam": 1048576, "estrategia": "best-fit" }


tam: tamaño de memoria en bytes.

estrategia: "first-fit" o "best-fit".

Solicitudes de memoria
"solicitudes_mem": [
  { "pid": 1, "tam": 120000 },
  { "pid": 2, "tam": 64000 }
]

📊 Salida esperada

El simulador genera:

Tabla de procesos con PID, Llegada, Servicio, Inicio, Fin, Respuesta, Espera y Retorno.

Resumen con promedios y throughput.

Asignación de memoria (bloque asignado o “no encontrado”).

Ejemplo:

PID | Llegada | Servicio | Inicio | Fin | Respuesta | Espera | Retorno
--------------------------------------------------------------------------------
  1 |       0 |       12 |      0 |  25 |         0 |     13 |      25
  2 |       1 |        5 |      4 |  17 |         3 |     11 |      16
  3 |       2 |        8 |      8 |  21 |         6 |     11 |      19

Resumen:
Promedio_Respuesta   : 3.00
Promedio_Espera      : 11.67
Promedio_Retorno     : 20.00
Throughput           : 0.12
Tiempo_Total         : 25

Asignación de memoria (estrategia: first-fit):
PID |       tam | bloque_inicio | tam_bloque
--------------------------------------------------
  1 |    120000 |             0 |     120000
  2 |     64000 |        120000 |      64000

📑 Créditos

Proyecto académico – Unidad 01: Simulador de Sistema Operativo.