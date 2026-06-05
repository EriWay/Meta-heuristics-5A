import time
from typing import List

from model.neighborhood import Neighborhood
from model.problem import Problem
from model.solution import Solution


class VNS:
    def __init__(self, problem: Problem, neighborhoods: List[Neighborhood] | None = None):
        self.problem = problem
        self.neighborhoods = neighborhoods or []

    def variable_neighborhood_search(self, initial_solution: Solution, max_time: float = 300):
        """Apply a time-bounded neighborhood search on a solution."""

        if not self.neighborhoods:
            return initial_solution

        print("\tValeur des solutions trouvées par VNS :")

        best_solution = initial_solution.deep_copy()
        current_solution = initial_solution.deep_copy()
        best_eval = best_solution.value()

        start_time = time.perf_counter()
        k = 0

        while (time.perf_counter() - start_time) <= max_time:
            improved = False

            while k < len(self.neighborhoods):
                if (time.perf_counter() - start_time) > max_time:
                    break

                print(f"\t\tNeighborhood {k + 1}")
                new_solution = self.neighborhoods[k].best_neighbor(current_solution)
                new_eval = new_solution.value()

                if new_eval < best_eval:
                    best_solution = new_solution.deep_copy()
                    current_solution = best_solution.deep_copy()
                    best_eval = new_eval
                    improved = True
                    print(f"\t\t{best_eval}")
                    k = 0
                else:
                    k += 1

            if (time.perf_counter() - start_time) > max_time:
                break

            if not improved:
                # Restart from a new feasible solution to avoid stopping after the first local optimum.
                current_solution = Solution.from_problem(self.problem)
                k = 0

        return best_solution


if __name__ == "__main__":
    print("Use __mainVNS__.py to run the VNS entry point.")
