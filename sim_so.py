from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import argparse, json

# ---------------------------
# PCB: Proceso (mínimo pedido)
# ---------------------------
@dataclass(order=True)
class Process:
    pid: int
    llegada: int
    servicio: int
    inicio: Optional[int] = None
    fin: Optional[int] = None
    restante: int = field(init=False, compare=False)

    def __post_init__(self):
        self.restante = self.servicio

    def metrics(self):
        if self.inicio is None or self.fin is None:
            raise ValueError("Proceso no finalizado: no hay métricas.")
        respuesta = self.inicio - self.llegada
        retorno = self.fin - self.llegada
        espera = retorno - self.servicio
        return {
            "PID": self.pid, "Llegada": self.llegada, "Servicio": self.servicio,
            "Inicio": self.inicio, "Fin": self.fin, "Respuesta": respuesta,
            "Espera": espera, "Retorno": retorno
        }

# ---------------------------
# Planificadores
# ---------------------------
class SchedulerBase:
    def select(self, ready: List[Process], t:int) -> Optional[Process]:
        raise NotImplementedError

class FCFS(SchedulerBase):
    def select(self, ready: List[Process], t:int) -> Optional[Process]:
        if not ready:
            return None
        return ready.pop(0)  # FIFO

class SPN(SchedulerBase):  # SJF no expropiativo
    def select(self, ready: List[Process], t:int) -> Optional[Process]:
        if not ready:
            return None
        idx = min(range(len(ready)),
                  key=lambda i: (ready[i].restante, ready[i].llegada, ready[i].pid))
        return ready.pop(idx)

class RR(SchedulerBase):
    def __init__(self, quantum:int):
        assert quantum >= 2, "Quantum debe ser ≥ 2"
        self.quantum = quantum
        self.time_slice_left = 0
        self.current: Optional[Process] = None

    def tick(self, ready: List[Process], t:int) -> Optional[Process]:
        # Despacho si la CPU está libre
        if self.current is None and ready:
            self.current = ready.pop(0)
            self.time_slice_left = self.quantum
            if self.current.inicio is None:
                self.current.inicio = t

        # Ejecuta 1 tick
        if self.current is not None:
            self.current.restante -= 1
            self.time_slice_left -= 1
            finished = False
            if self.current.restante == 0:
                self.current.fin = t + 1
                finished = True

            if finished:
                done = self.current
                self.current = None
                return done

            if self.time_slice_left == 0:
                # Expropiación y reencolado
                ready.append(self.current)
                self.current = None
        return None

# ---------------------------
# Motor de simulación de CPU
# ---------------------------
def simulate_cpu(processes: List[Process], policy:str, quantum:int=2, context_switch:int=0):
    arrivals = sorted(processes, key=lambda p: (p.llegada, p.pid))
    ready: List[Process] = []
    completed: List[Process] = []
    t = 0
    current: Optional[Process] = None
    rr = RR(quantum) if policy == "RR" else None

    while len(completed) < len(processes):
        # 1) Arribos
        while arrivals and arrivals[0].llegada == t:
            ready.append(arrivals.pop(0))

        if policy == "RR":
            done = rr.tick(ready, t)
            if done:
                completed.append(done)
                if context_switch > 0 and (rr.current is not None or ready):
                    t += context_switch
        else:
            # Despacho
            if current is None and ready:
                if policy == "FCFS":
                    current = FCFS().select(ready, t)
                elif policy == "SPN":
                    current = SPN().select(ready, t)
                else:
                    raise ValueError("Política desconocida")
                if current.inicio is None:
                    current.inicio = t

            # Ejecuta 1 tick
            if current is not None:
                current.restante -= 1
                if current.restante == 0:
                    current.fin = t + 1
                    completed.append(current)
                    current = None
                    if context_switch > 0 and ready:
                        t += context_switch

        t += 1

    # Métricas y resumen
    tabla = [p.metrics() for p in sorted(completed, key=lambda x: x.pid)]
    avg_resp = sum(r["Respuesta"] for r in tabla) / len(tabla)
    avg_wait = sum(r["Espera"] for r in tabla) / len(tabla)
    avg_turn = sum(r["Retorno"] for r in tabla) / len(tabla)
    total_time = max(r["Fin"] for r in tabla)
    throughput = len(tabla) / total_time if total_time > 0 else 0
    resumen = {
        "Promedio_Respuesta": avg_resp,
        "Promedio_Espera": avg_wait,
        "Promedio_Retorno": avg_turn,
        "Throughput": throughput,
        "Tiempo_Total": total_time
    }
    return tabla, resumen

# ---------------------------
# Gestión de memoria lineal
# ---------------------------
@dataclass
class Block:
    start: int
    size: int
    free: bool = True
    pid: Optional[int] = None

class MemoryManager:
    def __init__(self, size:int):
        self.size = size
        self.blocks: List[Block] = [Block(0, size, True, None)]

    def _coalesce(self):
        merged: List[Block] = []
        self.blocks.sort(key=lambda b: b.start)
        for b in self.blocks:
            if merged and merged[-1].free and b.free and merged[-1].start + merged[-1].size == b.start:
                merged[-1].size += b.size
            else:
                merged.append(b)
        self.blocks = merged

    def _find_first_fit(self, req:int) -> Optional[int]:
        for i, b in enumerate(self.blocks):
            if b.free and b.size >= req:
                return i
        return None

    def _find_best_fit(self, req:int) -> Optional[int]:
        best_idx = None
        best_size = None
        for i, b in enumerate(self.blocks):
            if b.free and b.size >= req:
                if best_size is None or b.size < best_size:
                    best_idx, best_size = i, b.size
        return best_idx

    def allocate(self, pid:int, req:int, strategy:str = "first-fit"):
        idx = self._find_first_fit(req) if strategy == "first-fit" else self._find_best_fit(req)
        if idx is None:
            return None
        b = self.blocks[idx]
        if b.size == req:
            b.free = False
            b.pid = pid
            chosen = b
        else:
            alloc = Block(b.start, req, False, pid)
            rest = Block(b.start + req, b.size - req, True, None)
            self.blocks[idx] = alloc
            self.blocks.insert(idx + 1, rest)
            chosen = alloc
        return {"bloque_inicio": chosen.start, "tam_bloque": chosen.size}

    def free_pid(self, pid:int):
        changed = False
        for b in self.blocks:
            if not b.free and b.pid == pid:
                b.free = True
                b.pid = None
                changed = True
        if changed:
            self._coalesce()
        return changed

# ---------------------------
# CLI
# ---------------------------
def run_from_config(config: Dict[str, Any]):
    # CPU
    cpu_cfg = config.get("cpu", {})
    alg = cpu_cfg.get("algoritmo", "FCFS")
    q = cpu_cfg.get("quantum", 2)
    if alg not in ("FCFS", "SPN", "RR"):
        raise ValueError("Algoritmo inválido (FCFS | SPN | RR).")
    if alg == "RR" and q < 2:
        raise ValueError("Quantum debe ser ≥ 2 para RR.")

    raw_procs = config.get("procesos", [])
    pids = set()
    processes = []
    for rp in raw_procs:
        pid = rp["pid"]; llegada = rp["llegada"]; servicio = rp["servicio"]
        if pid in pids:
            raise ValueError("PID duplicado.")
        if llegada < 0 or servicio < 1:
            raise ValueError("Llegada/Servicio inválidos.")
        pids.add(pid)
        processes.append(Process(pid=pid, llegada=llegada, servicio=servicio))

    tabla, resumen = simulate_cpu(processes, alg, q)

    # Salida CPU
    headers = ["PID","Llegada","Servicio","Inicio","Fin","Respuesta","Espera","Retorno"]
    print("PID | Llegada | Servicio | Inicio | Fin | Respuesta | Espera | Retorno")
    print("--- | ------- | -------- | ------ | --- | --------- | ------ | -------")
    for row in sorted(tabla, key=lambda r: r["PID"]):
        print(" | ".join(str(row[h]) for h in headers))

    print("\nResumen:")
    for k, v in resumen.items():
        print(f"- {k}: {v:.2f}" if isinstance(v, float) else f"- {k}: {v}")

    # Memoria
    mem_cfg = config.get("memoria", {})
    M = mem_cfg.get("tam", 1048576)
    strat = mem_cfg.get("estrategia", "first-fit")
    if strat not in ("first-fit", "best-fit"):
        raise ValueError("Estrategia de memoria inválida (first-fit | best-fit).")

    mm = MemoryManager(M)
    reqs = config.get("solicitudes_mem", [])

    print("\nAsignación de memoria:")
    for r in reqs:
        res = mm.allocate(r["pid"], r["tam"], strat)
        if res is None:
            print(f"- PID {r['pid']} tam={r['tam']}: no encontrado")
        else:
            print(f"- PID {r['pid']} tam={r['tam']}: bloque_inicio={res['bloque_inicio']} tam_bloque={res['tam_bloque']}")

def main():
    parser = argparse.ArgumentParser(description="Simulador de SO (CPU + Memoria)")
    parser.add_argument("--config", "-c", required=True, help="Ruta al archivo JSON de entrada")
    args = parser.parse_args()
    with open(args.config, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    run_from_config(cfg)

if __name__ == "__main__":
    main()
