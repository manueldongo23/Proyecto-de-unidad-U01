🖥️ Simulador de Sistema Operativo – Unidad 01



Proyecto académico que implementa un simulador básico de un sistema operativo.  

Permite poner en práctica los conceptos vistos en la Unidad 01 de \*\*Sistemas Operativos I\*\*:



\- Gestión de procesos con algoritmos de planificación: \*\*FCFS\*\*, \*\*SPN\*\* y \*\*Round Robin\*\*.  

\- Cálculo de métricas de desempeño: tiempo de respuesta, espera, retorno y throughput.  

\- Gestión de memoria con políticas \*\*First-Fit\*\* y \*\*Best-Fit\*\*.  



---



\## 🚀 Requisitos



\- Python 3.10 o superior  

\- Windows 10 u 11 (probado en ambos)  

\- Entorno virtual (`.venv`) activado  



---



\## 📂 Estructura del proyecto



sim-unidad01/

│

├── src/ # Código fuente (sim\_so.py)

├── config/ # Archivos JSON de configuración

├── docs/ # Informe técnico (PDF)

├── .gitignore # Exclusiones de Git

├── README.md # Este archivo

└── GUIA\_USUARIO.md # Instrucciones de uso detalladas



yaml

Copiar código



---



\## ⚙️ Uso básico



1\. Clonar o descargar el proyecto.  

&nbsp;  ```powershell

&nbsp;  git clone <url-del-repo>

&nbsp;  cd sim-unidad01

Crear y activar el entorno virtual:



powershell

Copiar código

python -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

Ejecutar el simulador con un archivo de configuración JSON:



powershell

Copiar código

python src\\sim\_so.py --config config\\ejemplo\_fcfs.json

🔄 Configuración rápida (JSON)

Los parámetros se definen en los archivos .json ubicados en la carpeta config/.



CPU

json

Copiar código

"cpu": { "algoritmo": "FCFS" }

Opciones: "FCFS", "SPN", "RR".



Si se usa "RR", es obligatorio añadir "quantum": 4 (mínimo 2).



Procesos

json

Copiar código

"procesos": \[

&nbsp; { "pid": 1, "llegada": 0, "servicio": 12 },

&nbsp; { "pid": 2, "llegada": 1, "servicio": 5 }

]

pid: identificador único.



llegada: tiempo de arribo.



servicio: tiempo total de CPU requerido.



Memoria

json

Copiar código

"memoria": { "tam": 1048576, "estrategia": "first-fit" }

tam: tamaño de memoria en bytes (ejemplo: 1048576 = 1 MiB).



estrategia: "first-fit" o "best-fit".



Solicitudes de memoria

json

Copiar código

"solicitudes\_mem": \[

&nbsp; { "pid": 1, "tam": 120000 },

&nbsp; { "pid": 2, "tam": 64000 }

]

pid: proceso solicitante.



tam: tamaño solicitado en bytes.



📊 Salida esperada

El simulador genera tres bloques de salida:



Tabla de procesos con métricas:



nginx

Copiar código

PID | Llegada | Servicio | Inicio | Fin | Respuesta | Espera | Retorno

&nbsp; 1 |       0 |       12 |      0 |  25 |         0 |     13 |      25

&nbsp; 2 |       1 |        5 |      4 |  17 |         3 |     11 |      16

&nbsp; 3 |       2 |        8 |      8 |  21 |         6 |     11 |      19

Resumen de métricas globales:



yaml

Copiar código

Promedio\_Respuesta   : 3.00

Promedio\_Espera      : 11.67

Promedio\_Retorno     : 20.00

Throughput           : 0.12

Tiempo\_Total         : 25

Asignación de memoria:



java

Copiar código

Asignación de memoria (estrategia: first-fit):

PID |       tam | bloque\_inicio | tam\_bloque

&nbsp; 1 |    120000 |             0 |     120000

&nbsp; 2 |     64000 |        120000 |      64000

