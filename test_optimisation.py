"""Compare les performances AVANT / APRES les voisinages non-conservatifs.
Lance directement :  python test_amelioration.py
"""
import os, sys, contextlib
from random import seed
from time import perf_counter
from file_io.importer import Importer
from model.solution import Solution
from solution.VND_Algo import VND
from solution.VNS_Algo import VNS
from model.neighborhood import (ChangeShiftNeighborhood, MoveBlockNeighborhood,
    TwoExchangeNeighborhood, DoubleExchangeNeighborhood,
    BlockExchangeNeighborhood, ThreeExchangeNeighborhood)

INSTANCE = 1        # numéro d'instance à tester
SEED = 42
VND_BUDGET = 60     # le VND s'arrête de lui-même bien avant
VNS_BUDGET = 15     # le VNS tourne tout le budget : monte-le pour des résultats plus fins


@contextlib.contextmanager
def quiet():
    """Masque les prints de progression des algos pour un affichage propre."""
    old = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    try:
        yield
    finally:
        sys.stdout.close()
        sys.stdout = old


def echanges(problem):
    return [TwoExchangeNeighborhood(problem), DoubleExchangeNeighborhood(problem),
            BlockExchangeNeighborhood(problem), ThreeExchangeNeighborhood(problem)]

def complet(problem):
    return [ChangeShiftNeighborhood(problem), MoveBlockNeighborhood(problem)] + echanges(problem)


def run(method, neigh_factory, problem):
    seed(SEED + INSTANCE)
    with quiet():
        sol = Solution.from_problem(problem)
    initiale = sol.value()
    t0 = perf_counter()
    with quiet():
        if method == "VND":
            algo = VND(problem, neigh_factory(problem))
            sol = algo.variable_neighborhood_descent(sol, VND_BUDGET)
        else:
            algo = VNS(problem, neigh_factory(problem))
            sol = algo.variable_neighborhood_search(sol, VNS_BUDGET)
    finale = sol.value()
    return initiale, finale, perf_counter() - t0, sol.is_feasible()


problem = Importer().import_problem(f"Instance{INSTANCE}.txt")
print(f"\n=== Instance {INSTANCE} "
      f"({len(problem.staff)} emp x {problem.days_count} j x {len(problem.shift_types)} shifts) ===")
print(f"{'configuration':30s}| {'initiale':>8s} | {'finale':>6s} | {'gain':>6s} | {'temps':>6s} | ok")
print("-" * 64)
for method in ["VND", "VNS"]:
    for label, fac in [("baseline (echanges)", echanges), ("+ ChangeShift+MoveBlock", complet)]:
        ini, fin, t, feas = run(method, fac, problem)
        gain = 100 * (ini - fin) / ini if ini else 0
        print(f"{(method+' '+label):30s}| {ini:8d} | {fin:6d} | {gain:5.1f}% | {t:5.1f}s | {feas}")
print("-" * 64)
print("(VND s'arrete de lui-meme ; VNS utilise tout le budget. "
      f"Monte VNS_BUDGET={VNS_BUDGET}s pour affiner.)")