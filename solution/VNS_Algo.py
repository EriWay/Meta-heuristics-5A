import os
import time
import contextlib
from random import sample, randrange
from typing import List

from model.neighborhood import Neighborhood
from model.problem import Problem
from model.solution import (Solution, set_days_off, assign_work_days,
                            is_personal_schedule_feasible)
from solution.VND_Algo import VND


def _regenerate_employee(problem: Problem, planning, e: int) -> None:
    """Regenere un planning individuel aleatoire FAISABLE pour l'employe e (in place).
    Reprend la logique de generation individuelle de Solution.generate_solution."""
    D = problem.days_count
    staff = problem.staff[e]
    max_tries = 100 * D
    schedule = [None] * D
    while not is_personal_schedule_feasible(schedule, problem, e):
        schedule = [None] * D
        schedule = set_days_off(problem, staff, schedule)
        schedule = assign_work_days(staff, schedule)
        available = staff.max_shift_days.copy()
        loops = 0
        while -1 in schedule:
            day = randrange(D)
            sh = randrange(len(available))
            if available[sh] > 0 and schedule[day] == -1:
                available[sh] -= 1
                schedule[day] = sh
            loops += 1
            if loops > max_tries:
                break
        worktime = sum(problem.shift_types[d].duration for d in schedule if d is not None)
        while worktime > staff.max_worktime:
            schedule[randrange(D)] = None
            worktime = sum(problem.shift_types[d].duration for d in schedule if d is not None)
    planning[e] = schedule


class VNS:
    def __init__(self, problem: Problem, neighborhoods: List[Neighborhood] | None = None):
        self.problem = problem
        self.neighborhoods = neighborhoods or []

    def variable_neighborhood_search(self, initial_solution: Solution, max_time: float = 300,
                                     print_interval: float = 10.0):
        """VNS canonique (GVNS).

        A chaque iteration :
          1. shaking : on perturbe la MEILLEURE solution en regenerant k employes au hasard
             (les N-k autres sont conserves) ; k est l'intensite de la perturbation.
          2. recherche locale : descente VND sur la solution perturbee.
          3. acceptation : si on ameliore, on adopte la solution et k revient a 1 ;
             sinon k augmente (perturbation plus forte). A k = N, on regenere tout
             (equivalent a un redemarrage aleatoire complet).
        """
        if not self.neighborhoods:
            return initial_solution

        print("\tValeur des solutions trouvées par VNS :")
        vnd = VND(self.problem, self.neighborhoods)
        nb_staff = len(self.problem.staff)

        best_solution = initial_solution.deep_copy()
        best_eval = best_solution.value()
        k = 1
        iteration = 0

        start_time = time.perf_counter()
        last_print = start_time
        while (time.perf_counter() - start_time) < max_time:
            iteration += 1

            # Heartbeat : signe d'activite en debut d'iteration (au plus une fois par print_interval)
            now = time.perf_counter()
            if now - last_print >= print_interval:
                print(f"\t\t  ... {now - start_time:5.0f}s | iter {iteration:4d} | k={k} | meilleure = {best_eval}")
                last_print = now

            # 1. Shaking : regenerer k employes de la meilleure solution
            shaken = best_solution.deep_copy()
            for e in sample(range(nb_staff), min(k, nb_staff)):
                _regenerate_employee(self.problem, shaken.planning, e)

            # 2. Recherche locale (VND) sur la solution perturbee
            remaining = max_time - (time.perf_counter() - start_time)
            if remaining <= 0:
                break
            with open(os.devnull, 'w') as devnull, contextlib.redirect_stdout(devnull):
                local = vnd.variable_neighborhood_descent(shaken, remaining)
            local_eval = local.value()

            # 3. Acceptation et mise a jour de l'intensite k
            if local_eval < best_eval:
                best_solution = local.deep_copy()
                best_eval = local_eval
                k = 1
                now = time.perf_counter()
                print(f"\t\t[{now - start_time:5.0f}s] iter {iteration:4d}  ->  meilleure = {best_eval}")
                last_print = now
            else:
                k = k + 1 if k < nb_staff else 1

        return best_solution


if __name__ == "__main__":
    print("Use __mainVNS__.py to run the VNS entry point.")