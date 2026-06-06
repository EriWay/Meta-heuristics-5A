"""This module defines the neighborhood structures used by the VND,
as defined by Rahimian et al., 2017
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


##

# def compare(best_value: int, best_solution: Solution, neighbor: Solution) -> Solution:
#     """Retourne la nouvelle meilleure """


class TwoExchangeNeighborhood(Neighborhood):
    """This neighborhood consists of all moves where two shifts are swapped
    between two different nurses on the same day."""

    def __init__(self, problem: Problem) -> None:
        super().__init__(problem)
    
    def best_neighbor(self, solution: Solution) -> Solution:
        # Variables
        best_solution: Solution = solution
        best_value: int = solution.value()

        # For all staff pairs
        for first_staff_int in range(len(self.problem.staff)):
            for second_staff_int in range(first_staff_int + 1, len(self.problem.staff)):
                
                first_planning = solution.planning[first_staff_int]
                second_planning = solution.planning[second_staff_int]

                # For all days
                for day in range(self.problem.days_count):

                    if first_planning[day] != second_planning[day]:
                        
                        neighbor: Solution = solution.deep_copy()
                        neighbor.planning[first_staff_int][day] = second_planning[day]
                        neighbor.planning[second_staff_int][day] = first_planning[day]
                        
                        if neighbor.is_feasible():
                            new_value = neighbor.value()
                            if new_value < best_value:
                                best_value = new_value
                                best_solution = neighbor
        
        return best_solution
    
class DoubleExchangeNeighborhood(Neighborhood):
    """This neighborhood includes all moves that swap 
    two shifts between two different nurses on two 
    different days."""

    def __init__(self, problem: Problem) -> None:
        super().__init__(problem)
    
    def best_neighbor(self, solution: Solution) -> Solution:
        # Variables
        best_solution: Solution = solution
        best_value: int = solution.value()

        # For all staff pairs
        for first_staff_int in range(len(self.problem.staff)):
            for second_staff_int in range(first_staff_int + 1, len(self.problem.staff)):
                
                first_planning = solution.planning[first_staff_int]
                second_planning = solution.planning[second_staff_int]

                # For all day pairs
                for first_day in range(self.problem.days_count):
                    for second_day in range(first_day + 1, self.problem.days_count):

                        neighbor: Solution = solution.deep_copy()
                        neighbor.planning[first_staff_int][first_day] = second_planning[first_day]
                        neighbor.planning[second_staff_int][first_day] = first_planning[first_day]
                        neighbor.planning[first_staff_int][second_day] = second_planning[second_day]
                        neighbor.planning[second_staff_int][second_day] = first_planning[second_day]
                        
                        if neighbor.is_feasible():
                            new_value = neighbor.value()
                            if new_value < best_value:
                                best_value = new_value
                                best_solution = neighbor
        
        return best_solution

class BlockExchangeNeighborhood(Neighborhood):
    """This neighborhood includes all moves where a
    specific number of consecutive shifts is swapped between two
    different nurses within the planning period."""

    def __init__(self, problem: Problem) -> None:
        super().__init__(problem)
    
    def best_neighbor(self, solution: Solution) -> Solution:
        # Variables
        best_solution: Solution = solution
        best_value: int = solution.value()

        # For all staff pairs
        for first_staff_int in range(len(self.problem.staff)):
            for second_staff_int in range(first_staff_int + 1, len(self.problem.staff)):
                
                first_planning = solution.planning[first_staff_int]
                second_planning = solution.planning[second_staff_int]

                # For all day pairs
                for first_day in range(self.problem.days_count):
                    for second_day in range(first_day + 1, self.problem.days_count):

                        neighbor: Solution = solution.deep_copy()
                        neighbor.planning[first_staff_int][first_day:second_day + 1] = second_planning[first_day:second_day + 1]
                        neighbor.planning[second_staff_int][first_day:second_day + 1] = first_planning[first_day:second_day + 1]
                        
                        if neighbor.is_feasible():
                            new_value = neighbor.value()
                            if new_value < best_value:
                                best_value = new_value
                                best_solution = neighbor
        
        return best_solution

class ThreeExchangeNeighborhood(Neighborhood):
    """This neighborhood includes all moves, where three 
    shifts are exchanged between three different nurses 
    on the same day."""

    def __init__(self, problem: Problem) -> None:
        super().__init__(problem)
    
    def best_neighbor(self, solution: Solution) -> Solution:
        # Variables
        best_solution: Solution = solution
        best_value: int = solution.value()

        # For all sets of 3 staff
        for first_staff_int in range(len(self.problem.staff)):
            for second_staff_int in range(first_staff_int + 1, len(self.problem.staff)):
                for third_staff_int in range(second_staff_int + 1, len(self.problem.staff)):
                
                    # first_planning = solution.planning[first_staff_int]
                    # second_planning = solution.planning[second_staff_int]

                    # For all days
                    for day in range(self.problem.days_count):

                        for neighbor in self._get_neighbors((first_staff_int, second_staff_int, third_staff_int),
                                                            day, solution):
                            
                            if neighbor.is_feasible():
                                new_value = neighbor.value()
                                if new_value < best_value:
                                    best_value = new_value
                                    best_solution = neighbor
        
        return best_solution

    @staticmethod
    def _get_neighbors(staff_ints: Tuple[int, int, int], day: int, solution: Solution):

        neighbor: Solution = solution.deep_copy()

        # backward move
        neighbor.planning[staff_ints[0]][day] = solution.planning[staff_ints[1]][day]
        neighbor.planning[staff_ints[1]][day] = solution.planning[staff_ints[2]][day]
        neighbor.planning[staff_ints[2]][day] = solution.planning[staff_ints[0]][day]

        yield neighbor

        neighbor = solution.deep_copy()

        # forward move
        neighbor.planning[staff_ints[0]][day] = solution.planning[staff_ints[2]][day]
        neighbor.planning[staff_ints[1]][day] = solution.planning[staff_ints[0]][day]
        neighbor.planning[staff_ints[2]][day] = solution.planning[staff_ints[1]][day]

        yield neighbor




class ChangeShiftNeighborhood(Neighborhood):
    """Voisinage NON conservatif : change le shift d'un seul employe sur un jour
    (assigner, retirer, ou remplacer). Modifie la couverture, contrairement aux echanges."""

    def __init__(self, problem: Problem) -> None:
        super().__init__(problem)

    def best_neighbor(self, solution: Solution) -> Solution:
        nb_staff = len(self.problem.staff)
        nb_days = self.problem.days_count
        candidate_values = [None] + list(range(len(self.problem.shift_types)))
        best_delta, best_move = 0, None
        for e in range(nb_staff):
            for d in range(nb_days):
                current = solution.planning[e][d]
                for new_s in candidate_values:
                    if new_s == current:
                        continue
                    delta = move_delta(solution, [(e, d, new_s)])
                    if delta < best_delta:
                        old = solution.planning[e][d]
                        solution.planning[e][d] = new_s
                        feasible = is_feasible_local(solution, [e])
                        solution.planning[e][d] = old
                        if feasible:
                            best_delta, best_move = delta, (e, d, new_s)
        if best_move is None:
            return solution
        neighbor = solution.deep_copy()
        e, d, new_s = best_move
        neighbor.planning[e][d] = new_s
        return neighbor

def _blocks_of(sched):
    blocks, i, D = [], 0, len(sched)
    while i < D:
        if sched[i] is not None:
            j = i
            while j < D and sched[j] is not None:
                j += 1
            blocks.append((i, j - 1, sched[i:j]));
            i = j
        else:
            i += 1
    return blocks

class MoveBlockNeighborhood(Neighborhood):
    """Voisinage NON conservatif : deplace un bloc de travail entier vers une position
    libre. Preserve la longueur du bloc (donc min/max consecutifs) tout en deplacant
    la couverture vers d'autres jours."""

    def __init__(self, problem: Problem) -> None:
        super().__init__(problem)

    def best_neighbor(self, solution: Solution) -> Solution:
        best_delta, best_changes = 0, None
        N, D = len(self.problem.staff), self.problem.days_count
        for e in range(N):
            sched = solution.planning[e]
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
                    delta = move_delta(solution, change_list)
                    if delta < best_delta:
                        olds = [(e, d, solution.planning[e][d]) for (e, d, _) in change_list]
                        for (e_, d, ns) in change_list:
                            solution.planning[e_][d] = ns
                        feas = is_feasible_local(solution, [e])
                        for (e_, d, os_) in olds:
                            solution.planning[e_][d] = os_
                        if feas:
                            best_delta, best_changes = delta, change_list
        if best_changes is None:
            return solution
        neighbor = solution.deep_copy()
        for (e, d, ns) in best_changes:
            neighbor.planning[e][d] = ns
        return neighbor