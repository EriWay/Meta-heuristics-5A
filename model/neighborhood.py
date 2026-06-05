"""This module defines the neighborhood structures used by the VND,
as defined by Rahimian et al., 2017
"""

from model.problem import Problem
from model.solution import Solution
from typing import Tuple

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