"""This module defines the neighborhood structures used by the VND,
as defined by Rahimian et al., 2017

Tous les voisinages evaluent chaque mouvement candidat par delta-evaluation
(move_delta) et faisabilite locale (is_feasible_local), puis n'effectuent
qu'une seule copie profonde pour le meilleur mouvement retenu.
"""

from model.problem import Problem
from typing import Tuple
from model.solution import Solution, move_delta, is_feasible_local


class Neighborhood:
    """Interface for implementing neighborhoods structures."""
    
    def __init__(self, problem: Problem) -> None:
        self.problem = problem

    def best_neighbor(self, solution: Solution) -> Solution:
        """Return best neighbor of solution in this neighborhood structure."""
        pass


def _apply_best(solution: Solution, best_move):
    """Retourne une copie de solution avec le meilleur mouvement applique."""
    if best_move is None:
        return solution
    neighbor = solution.deep_copy()
    for (e, d, ns) in best_move:
        neighbor.planning[e][d] = ns
    return neighbor


def _evaluate(solution: Solution, changes, touched, best_delta, best_move):
    """Evalue un mouvement (changes) par delta + faisabilite locale.
    Retourne (best_delta, best_move) mis a jour si le mouvement est meilleur."""
    delta = move_delta(solution, changes)
    if delta < best_delta:
        plan = solution.planning
        olds = [(e, d, plan[e][d]) for (e, d, _) in changes]
        for (e, d, ns) in changes:
            plan[e][d] = ns
        feasible = is_feasible_local(solution, touched)
        for (e, d, os_) in olds:
            plan[e][d] = os_
        if feasible:
            return delta, changes
    return best_delta, best_move


class TwoExchangeNeighborhood(Neighborhood):
    """Echange du shift entre deux employes sur un meme jour."""
    def __init__(self, problem: Problem) -> None:
        super().__init__(problem)
    
    def best_neighbor(self, solution: Solution) -> Solution:
        plan = solution.planning
        N, D = len(self.problem.staff), self.problem.days_count
        best_delta, best_move = 0, None
        for a in range(N):
            for b in range(a + 1, N):
                for day in range(D):
                    if plan[a][day] != plan[b][day]:
                        changes = [(a, day, plan[b][day]), (b, day, plan[a][day])]
                        best_delta, best_move = _evaluate(solution, changes, (a, b), best_delta, best_move)
        return _apply_best(solution, best_move)


class DoubleExchangeNeighborhood(Neighborhood):
    """Echange des shifts entre deux employes sur deux jours differents."""
    def __init__(self, problem: Problem) -> None:
        super().__init__(problem)
    
    def best_neighbor(self, solution: Solution) -> Solution:
        plan = solution.planning
        N, D = len(self.problem.staff), self.problem.days_count
        best_delta, best_move = 0, None
        for a in range(N):
            for b in range(a + 1, N):
                for d1 in range(D):
                    for d2 in range(d1 + 1, D):
                        changes = [(a, d1, plan[b][d1]), (b, d1, plan[a][d1]),
                                   (a, d2, plan[b][d2]), (b, d2, plan[a][d2])]
                        best_delta, best_move = _evaluate(solution, changes, (a, b), best_delta, best_move)
        return _apply_best(solution, best_move)


class BlockExchangeNeighborhood(Neighborhood):
    """Echange d'un bloc de jours consecutifs entre deux employés."""
    def __init__(self, problem: Problem) -> None:
        super().__init__(problem)
    
    def best_neighbor(self, solution: Solution) -> Solution:
        plan = solution.planning
        N, D = len(self.problem.staff), self.problem.days_count
        best_delta, best_move = 0, None
        for a in range(N):
            for b in range(a + 1, N):
                for d1 in range(D):
                    for d2 in range(d1 + 1, D):
                        changes = []
                        for d in range(d1, d2 + 1):
                            changes.append((a, d, plan[b][d]))
                            changes.append((b, d, plan[a][d]))
                        best_delta, best_move = _evaluate(solution, changes, (a, b), best_delta, best_move)
        return _apply_best(solution, best_move)


class ThreeExchangeNeighborhood(Neighborhood):
    """Rotation circulaire (forward + backward) entre trois employes sur un meme jour."""
    def __init__(self, problem: Problem) -> None:
        super().__init__(problem)
    
    def best_neighbor(self, solution: Solution) -> Solution:
        plan = solution.planning
        N, D = len(self.problem.staff), self.problem.days_count
        best_delta, best_move = 0, None
        for a in range(N):
            for b in range(a + 1, N):
                for c in range(b + 1, N):
                    for day in range(D):
                        # backward : a<-b, b<-c, c<-a
                        bwd = [(a, day, plan[b][day]), (b, day, plan[c][day]), (c, day, plan[a][day])]
                        best_delta, best_move = _evaluate(solution, bwd, (a, b, c), best_delta, best_move)
                        # forward : a<-c, b<-a, c<-b
                        fwd = [(a, day, plan[c][day]), (b, day, plan[a][day]), (c, day, plan[b][day])]
                        best_delta, best_move = _evaluate(solution, fwd, (a, b, c), best_delta, best_move)
        return _apply_best(solution, best_move)


class ChangeShiftNeighborhood(Neighborhood):
    """Voisinage NON conservatif : change le shift d'un seul employe sur un jour
    (assigner, retirer, ou remplacer). Modifie la couverture, contrairement aux echanges."""

    def __init__(self, problem: Problem) -> None:
        super().__init__(problem)

    def best_neighbor(self, solution: Solution) -> Solution:
        plan = solution.planning
        N, D = len(self.problem.staff), self.problem.days_count
        candidate_values = [None] + list(range(len(self.problem.shift_types)))
        best_delta, best_move = 0, None
        for e in range(N):
            for d in range(D):
                current = plan[e][d]
                for new_s in candidate_values:
                    if new_s == current:
                        continue
                    best_delta, best_move = _evaluate(solution, [(e, d, new_s)], (e,), best_delta, best_move)
        return _apply_best(solution, best_move)


def _blocks_of(sched):
    blocks, i, D = [], 0, len(sched)
    while i < D:
        if sched[i] is not None:
            j = i
            while j < D and sched[j] is not None:
                j += 1
            blocks.append((i, j - 1, sched[i:j])); i = j
        else:
            i += 1
    return blocks


class MoveBlockNeighborhood(Neighborhood):
    """Voisinage NON conservatif : deplace un bloc de travail entier vers une position
    libre. Preserve la longueur du bloc tout en deplacant la couverture."""

    def __init__(self, problem: Problem) -> None:
        super().__init__(problem)

    def best_neighbor(self, solution: Solution) -> Solution:
        plan = solution.planning
        N, D = len(self.problem.staff), self.problem.days_count
        best_delta, best_move = 0, None
        for e in range(N):
            sched = plan[e]
            for (a, b, shift_list) in _blocks_of(sched):
                length = b - a + 1
                old_days = set(range(a, b + 1))
                for a2 in range(0, D - length + 1):
                    if a2 == a:
                        continue
                    if any(sched[d] is not None and d not in old_days
                           for d in range(a2, a2 + length)):
                        continue
                    changes = {d: None for d in range(a, b + 1)}
                    for k in range(length):
                        changes[a2 + k] = shift_list[k]
                    change_list = [(e, d, ns) for d, ns in changes.items()]
                    best_delta, best_move = _evaluate(solution, change_list, (e,), best_delta, best_move)
        return _apply_best(solution, best_move)