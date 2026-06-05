import time

from model.problem import Problem
from model.solution import Solution
from model.neighborhood import Neighborhood
from typing import List

class VND:
    def __init__(self, problem: Problem, neighborhoods: List[Neighborhood]):
        self.problem: Problem = problem
        self.neighborhoods: List[Neighborhood] = neighborhoods

    def variable_neighborhood_descent(self, initial_solution: Solution, max_time: float = 300):
        """Fonction de l'algorithme VND."""
        print("\tValeur des solutions trouvées par VND :")

        # Initialisation de la liste pour stocker les solutions
        # all_solutions = []
        best_solution = initial_solution
        best_eval = best_solution.value()
        start_time = time.perf_counter()

        k = 0
        while k < len(self.neighborhoods):
            print(f"\t\tNeighborhood {k + 1}")
            new_solution = self.neighborhoods[k].best_neighbor(best_solution)
            # current_eval = self.evaluate(current_solution)
            new_eval = new_solution.value()

            if new_eval < best_eval:
                best_solution = new_solution
                best_eval = new_eval
                print(f"\t\t{best_eval}")
                k = 0
            else:
                k += 1
                # all_solutions.append(current_solution.copy())  # Stocker la nouvelle solution
                #retouner la liste des solutions à chaque fois. Au cas où le nombre d'itération est grand, on garde la liste des solutions
                # return all_solutions  
            
            if (time.perf_counter() - start_time) > max_time:
                break

        return best_solution


# Exemple d'utilisation
if __name__ == "__main__":
    # Création d'une instance du problème
    problem_instance = Problem(days_count=7)

    # Initialisation de la métaheuristique VND
    vnd = VND(problem_instance)

    # Paramètre de la VND
    max_k = 5   # max d'itérations pour la recherche locale

    # Application de la VND
    best_solution = vnd.variable_neighborhood_descent(max_k)

    # Affichage de la solution optimale
    print("Best Solution:", best_solution)
    print("Best Evaluation:", vnd.evaluate(best_solution))
