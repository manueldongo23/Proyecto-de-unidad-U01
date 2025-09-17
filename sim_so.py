# sim_so.py
import json
import argparse
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from collections import deque

# =========================
# 1) Modelo de Proceso (PCB)
# =========================
@dataclass
class Process:
    pid: int
    llegada: int
    servicio: int
    inicio: Optional[int] = None
    fin: Optional[int] = None
    restante: int = field(init=False)

    def __post_init__(self):
        self.restante = self.servicio


# =========================
# 2) Planificadores de CPU
# =========================
def fcfs(procesos: List[Process]) -> List[Process]:
    t = 0
    orden = sorted(procesos, key=lambda p: (p.llegada, p.pid))
    for p in orden:
        if t < p.llegada:
            t = p.llegada
        p.inicio = t
        t += p.servicio
        p.fin = t
    return orden

def spn(procesos: List[Process]) -> List[Process]:
    t = 0
    pendientes = sorted(procesos, key=lambda p: (p.llegada, p.pid))
    ready: List[Process] = []
    terminados: List[Process] = []

    while pendientes or ready:
        while pendientes and pendientes[0].llegada <= t:
            ready.append(pendientes.pop(0))
        if not ready:
            # nadie listo: saltamos al próximo arribo
            t = pendientes[0].llegada
            continue
        # menor servicio; empate -> menor llegada -> menor pid
        ready.sort(key=lambda p: (p.servicio, p.llegada, p.pid))
        p = ready.pop(0)
        if p.inicio is None:
            p.inicio = t
        t += p.servicio
        p.fin = t
        terminados.append(p)
    return terminados

def rr(procesos: List[Process], quantum: int) -> List[Process]:
    if quantum < 2:
        raise ValueError("Quantum debe ser ≥ 2 para RR.")
    t = 0
    llegada_orden = sorted(procesos, key=lambda p: (p.llegada, p.pid))
    i = 0
    cola = deque()
    terminados: List[Process] = []

    while i < len(llegada_orden) or cola:
        # encolar los que llegaron hasta t
        while i < len(llegada_orden) and llegada_orden[i].llegada <= t:
            cola.append(llegada_orden[i])
            i += 1
        if not cola:
            # saltar al próximo arribo
            t = llegada_orden[i].llegada
            continue

        p = cola.popleft()
        if p.inicio is None:
            p.inicio = t
        run = min(quantum, p.restante)
        t += run
        p.restante -= run

        # llegan procesos mientras corre el quantum
        while i < len(llegada_orden) and llegada_orden[i].llegada <= t:
            cola.append(llegada_orden[i])
            i += 1

        if p.restante > 0:
            cola.append(p)      # reencolar
        else:
            p.fin = t
            terminados.append(p)

    return terminados


# =========================
# 3) Cálculo de métricas
# =========================
def calcular_metricas(finalizados: List[Process]):
    tabla = []
    tot_resp = tot_esp = tot_ret = 0
    for p in finalizados:
        resp = p.inicio - p.llegada
        ret = p.fin - p.llegada
        esp = ret - p.servicio
        tot_resp += resp
        tot_esp += esp
        tot_ret += ret
        tabla.append({
            "PID": p.pid, "Llegada": p.llegada, "Servicio": p.servicio,
            "Inicio": p.inicio, "Fin": p.fin, "Respuesta": resp,
            "Espera": esp, "Retorno": ret
        })
    n = len(finalizados)
    t_total = max(p.fin for p in finalizados) if n else 0
    resumen = {
        "Promedio_Respuesta": tot_resp / n if n else 0.0,
        "Promedio_Espera":    tot_esp  / n if n else 0.0,
        "Promedio_Retorno":   tot_ret  / n if n else 0.0,
        "Throughput": (n / t_total) if t_total else 0.0,
        "Tiempo_Total": t_total
    }
    return tabla, resumen


# =========================
# 4) Memoria lineal (FF/BF)
# =========================
@dataclass
class Block:
    start: int
    size: int
    free: bool = True
    pid: Optional[int] = None

class MemoryManager:
    def __init__(self, size: int):
        self.blocks: List[Block] = [Block(0, size, True, None)]

    def _find_first_fit(self, req: int) -> Optional[int]:
        for i, b in enumerate(self.blocks):
            if b.free and b.size >= req:
                return i
        return None

    def _find_best_fit(self, req: int) -> Optional[int]:
        best_idx, best_size = None, None
        for i, b in enumerate(self.blocks):
            if b.free and b.size >= req:
                if best_size is None or b.size < best_size:
                    best_idx, best_size = i, b.size
        return best_idx

    def allocate(self, pid: int, req: int, strategy: str):
        idx = self._find_first_fit(req) if strategy == "first-fit" else self._find_best_fit(req)
        if idx is None:
            return None  # no encontrado
        b = self.blocks[idx]
        if b.size == req:
            b.free = False
            b.pid = pid
            chosen = b
        else:
            # split
            chosen = Block(b.start, req, False, pid)
            rest = Block(b.start + req, b.size - req, True, None)
            self.blocks[idx] = chosen
            self.blocks.insert(idx + 1, rest)
        return {"bloque_inicio": chosen.start, "tam_bloque": chosen.size}


# =========================
# 5) Impresión ordenada
# =========================
def imprimir_tabla(tabla: List[Dict]):
    print(f"{'PID':>3} | {'Llegada':>7} | {'Servicio':>8} | {'Inicio':>6} | {'Fin':>3} | {'Respuesta':>9} | {'Espera':>6} | {'Retorno':>7}")
    print("-"*86)
    for r in sorted(tabla, key=lambda x: x["PID"]):
        print(f"{r['PID']:>3} | {r['Llegada']:>7} | {r['Servicio']:>8} | {r['Inicio']:>6} | {r['Fin']:>3} | {r['Respuesta']:>9} | {r['Espera']:>6} | {r['Retorno']:>7}")

def imprimir_resumen(resumen: Dict):
    print("\nResumen:")
    print(f"{'Promedio_Respuesta':<20}: {resumen['Promedio_Respuesta']:.2f}")
    print(f"{'Promedio_Espera':<20}: {resumen['Promedio_Espera']:.2f}")
    print(f"{'Promedio_Retorno':<20}: {resumen['Promedio_Retorno']:.2f}")
    print(f"{'Throughput':<20}: {resumen['Throughput']:.2f}")
    print(f"{'Tiempo_Total':<20}: {resumen['Tiempo_Total']}")

def imprimir_mem_asignaciones(mm: MemoryManager, solicitudes: List[Dict], estrategia: str):
    print(f"\nAsignación de memoria (estrategia: {estrategia}):")
    print(f"{'PID':>3} | {'tam':>9} | {'bloque_inicio':>13} | {'tam_bloque':>10}")
    print("-"*50)
    for r in solicitudes:
        res = mm.allocate(r["pid"], r["tam"], estrategia)
        if res is None:
            print(f"{r['pid']:>3} | {r['tam']:>9} | {'no encontrado':>13} | {'-':>10}")
        else:
            print(f"{r['pid']:>3} | {r['tam']:>9} | {res['bloque_inicio']:>13} | {res['tam_bloque']:>10}")


# =========================
# 6) Orquestador (lee JSON)
# =========================
def run_from_config(path: str):
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    cpu_cfg = cfg.get("cpu", {})
    alg = cpu_cfg.get("algoritmo", "FCFS").upper()
    quantum = int(cpu_cfg.get("quantum", 2))

    procs = []
    seen = set()
    for p in cfg.get("procesos", []):
        pid, llegada, servicio = p["pid"], p["llegada"], p["servicio"]
        if pid in seen:
            raise ValueError("PID duplicado en entrada.")
        if llegada < 0 or servicio < 1:
            raise ValueError("Llegada/Servicio inválidos.")
        seen.add(pid)
        procs.append(Process(pid, llegada, servicio))

    if alg == "FCFS":
        finalizados = fcfs(procs)
    elif alg == "SPN":
        finalizados = spn(procs)
    elif alg == "RR":
        finalizados = rr(procs, quantum)
    else:
        raise ValueError("Algoritmo inválido. Use FCFS | SPN | RR")

    tabla, resumen = calcular_metricas(finalizados)
    imprimir_tabla(tabla)
    imprimir_resumen(resumen)

    mem_cfg = cfg.get("memoria", {})
    M = int(mem_cfg.get("tam", 1048576))
    estrategia = mem_cfg.get("estrategia", "first-fit").lower()
    if estrategia not in ("first-fit", "best-fit"):
        raise ValueError("Estrategia de memoria inválida (first-fit | best-fit).")
    mm = MemoryManager(M)
    imprimir_mem_asignaciones(mm, cfg.get("solicitudes_mem", []), estrategia)


# =========================
# 7) Main
# =========================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulador SO: CPU (FCFS/SPN/RR) + Memoria (FF/BF)")
    parser.add_argument("--config", "-c", required=True, help="Ruta a archivo JSON de entrada")
    args = parser.parse_args()
    run_from_config(args.config)
