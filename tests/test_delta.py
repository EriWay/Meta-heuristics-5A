"""Test/démo de l'étape 3 : delta-évaluation + faisabilité locale.
Lance directement :  python test_delta.py    (ou via pytest)
"""
from random import seed, randrange, choice
from time import perf_counter
from copy import deepcopy
from file_io.importer import Importer
from model.solution import Solution, move_delta, is_feasible_local

INSTANCE = 13   # change ce numéro pour tester une autre instance


def random_move(sol):
    N, D, S = len(sol.problem.staff), sol.problem.days_count, len(sol.problem.shift_types)
    if randrange(2) == 0:
        a, b, d = randrange(N), randrange(N), randrange(D)
        return [(a, d, sol.planning[b][d]), (b, d, sol.planning[a][d])]
    e, d = randrange(N), randrange(D)
    return [(e, d, choice([None] + list(range(S))))]


def _load():
    seed(100 + INSTANCE)
    return Solution.from_problem(Importer().import_problem(f"Instance{INSTANCE}.txt"))


def test_delta_exact():
    sol = _load(); V = sol.value()
    for _ in range(3000):
        ch = random_move(sol); d = move_delta(sol, ch)
        for (e, day, ns) in ch: sol.planning[e][day] = ns
        V2 = sol.value(); assert V2 - V == d; V = V2


def test_feasibilite_locale():
    sol = _load()
    for _ in range(500):
        ch = random_move(sol)
        olds = [(e, day, sol.planning[e][day]) for (e, day, _) in ch]
        for (e, day, ns) in ch: sol.planning[e][day] = ns
        assert sol.is_feasible() == is_feasible_local(sol, {e for (e, day, _) in ch})
        for (e, day, os_) in olds: sol.planning[e][day] = os_


def _demo():
    print(f"\n=== DEMO sur l'instance {INSTANCE} ===")
    sol = _load()
    print(f"Valeur de depart : {sol.value()}\n")
    print("Mouvements : delta calcule (rapide) vs reel (recalcul complet)")
    print("-" * 60)
    ok = True
    for i in range(6):
        ch = random_move(sol); before = sol.value()
        d = move_delta(sol, ch)
        for (e, day, ns) in ch: sol.planning[e][day] = ns
        reel = sol.value() - before
        if reel != d: ok = False
        kind = "echange" if len(ch) == 2 else "1 shift"
        print(f"  move {i+1} ({kind}): delta={d:+5d} | reel={reel:+5d}  -> {'OK' if reel==d else 'ERREUR'}")
    print("-" * 60)

    errors = 0; sol = _load(); V = sol.value()
    for _ in range(3000):
        ch = random_move(sol); d = move_delta(sol, ch)
        for (e, day, ns) in ch: sol.planning[e][day] = ns
        V2 = sol.value()
        if V2 - V != d: errors += 1
        V = V2
    print(f"\n  Exactitude du delta : {errors} erreur(s) / 3000 mouvements")

    sol = _load(); mism = 0
    for _ in range(500):
        ch = random_move(sol)
        olds = [(e, day, sol.planning[e][day]) for (e, day, _) in ch]
        for (e, day, ns) in ch: sol.planning[e][day] = ns
        if sol.is_feasible() != is_feasible_local(sol, {e for (e, day, _) in ch}): mism += 1
        for (e, day, os_) in olds: sol.planning[e][day] = os_
    print(f"  Faisabilite locale  : {mism} divergence(s) / 500 mouvements")

    sol = _load(); moves = [random_move(sol) for _ in range(2000)]
    t0 = perf_counter()
    for ch in moves: move_delta(sol, ch)
    t_delta = perf_counter() - t0
    base = deepcopy(sol.planning); t0 = perf_counter()
    for ch in moves:
        for (e, day, ns) in ch: sol.planning[e][day] = ns
        sol.value(); sol.planning = deepcopy(base)
    t_full = perf_counter() - t0
    print(f"\n  Vitesse : delta {t_delta*1000:.0f} ms vs complet {t_full*1000:.0f} ms "
          f"-> x{t_full/t_delta:.0f} plus rapide")
    print(f"\n=== VERDICT : {'TOUT EST BON' if errors==0 and mism==0 and ok else 'PROBLEME'} ===\n")


if __name__ == "__main__":
    _demo()