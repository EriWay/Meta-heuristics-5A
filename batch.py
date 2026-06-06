"""Batch : lance VND et VNS sur un ensemble d'instances et produit un tableau + un CSV.
Lance directement :  python batch.py
Les resultats sont ecrits ligne par ligne dans batch_results.csv (rien n'est perdu si ca s'interrompt).
"""
import os, sys, csv, time, contextlib
from random import seed
from file_io.importer import Importer
from model.solution import Solution
from solution.VND_Algo import VND
from solution.VNS_Algo import VNS
from model.neighborhood import (ChangeShiftNeighborhood, MoveBlockNeighborhood,
    TwoExchangeNeighborhood, DoubleExchangeNeighborhood,
    BlockExchangeNeighborhood, ThreeExchangeNeighborhood)

INSTANCES = range(1, 25)   # instances a tester (1 a 24)
SEED = 42
VND_BUDGET = 60            # le VND s'arrete de lui-meme avant
VNS_BUDGET = 180            # temps alloue au VNS par instance (secondes)
OUTPUT_CSV = "batch_results.csv"


@contextlib.contextmanager
def quiet():
    old = sys.stdout; sys.stdout = open(os.devnull, 'w')
    try: yield
    finally: sys.stdout.close(); sys.stdout = old

def neighborhoods(pb):
    return [ChangeShiftNeighborhood(pb), MoveBlockNeighborhood(pb), TwoExchangeNeighborhood(pb),
            DoubleExchangeNeighborhood(pb), BlockExchangeNeighborhood(pb), ThreeExchangeNeighborhood(pb)]

def gain(ini, fin):
    return 100 * (ini - fin) / ini if ini else 0.0

header = ["instance", "staff", "days", "shifts", "initiale",
          "VND_final", "VND_gain%", "VND_temps_s", "VNS_final", "VNS_gain%", "VNS_temps_s"]

print(f"{'inst':>4} | {'taille':>12} | {'init':>6} | {'VND':>6} {'gain':>6} {'t(s)':>6} | {'VNS':>6} {'gain':>6} {'t(s)':>6}")
print("-" * 86)

with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    f.flush()
    for inst in INSTANCES:
        try:
            pb = Importer().import_problem(f"Instance{inst}.txt")
            N, D, S = len(pb.staff), pb.days_count, len(pb.shift_types)

            seed(SEED + inst)
            with quiet(): s0 = Solution.from_problem(pb)
            ini = s0.value()

            t0 = time.perf_counter()
            with quiet(): sv = VND(pb, neighborhoods(pb)).variable_neighborhood_descent(s0.deep_copy(), VND_BUDGET)
            vnd_t = time.perf_counter() - t0
            vnd_val = sv.value()

            seed(SEED + inst)
            t0 = time.perf_counter()
            with quiet(): sw = VNS(pb, neighborhoods(pb)).variable_neighborhood_search(s0.deep_copy(), VNS_BUDGET)
            vns_t = time.perf_counter() - t0
            vns_val = sw.value()

            writer.writerow([inst, N, D, S, ini, vnd_val, f"{gain(ini,vnd_val):.1f}", f"{vnd_t:.1f}",
                             vns_val, f"{gain(ini,vns_val):.1f}", f"{vns_t:.1f}"])
            f.flush()
            print(f"{inst:>4} | {f'{N}x{D}x{S}':>12} | {ini:>6} | {vnd_val:>6} {gain(ini,vnd_val):>5.1f}% {vnd_t:>6.1f} | "
                  f"{vns_val:>6} {gain(ini,vns_val):>5.1f}% {vns_t:>6.1f}")
        except Exception as e:
            print(f"{inst:>4} | ERREUR : {e}")

print("-" * 86)
print(f"Resultats ecrits dans {OUTPUT_CSV}")