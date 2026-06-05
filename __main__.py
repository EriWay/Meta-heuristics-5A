from model.solution import Solution
from file_io.export_solution import Solution2file
from file_io.importer import Importer
from solution.VND_Algo import VND
from model.neighborhood import *
from model.problem import Problem
from datetime import datetime
from time import perf_counter
from typing import List
import os, os.path
import errno

def info_provider(solution: Solution):

        # date du jouts
        date_heure_actuelles = datetime.now()
        date = date_heure_actuelles.strftime("%d/%m/%Y %H:%M:%S")
        authors = "3W3nn PM & Eriway Dvx"
        algorithm = "Variable Neighborhood Descent"

        # Convertissez les différences en heures, minutes et secondes
        cpu_hours, cpu_remainder = divmod(solution.cpu_time, 3600)
        cpu_minutes, cpu_seconds = divmod(cpu_remainder, 60)
        cpu_time = "{:02} Heures {:02} minutes {:02} secondes".format(int(cpu_hours), int(cpu_minutes), int(cpu_seconds))

        informations = [
                        ("SchedulingPeriodFile", f"./examples/instances/{solution.path_to_problem[:-4]}.ros"),
                        ("Penalty",f"{solution.value()}"),
                        ("DateFound",date),
                        ("FoundBy",authors),
                        ("Algorithm",algorithm),
                        ("CpuTime",cpu_time) ]
        
        return informations

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: 
            raise


### Tests sur les instances ###

TEMPS_MAX_PAR_INSTANCE: float = 300 # en secondes
INSTANCES_A_TESTER: int = 1 # tester les instances 1 à n

test_datetime = datetime.now()
folder_name = test_datetime.strftime("%Y-%m-%d_%H-%M-%S")
relative_path = f"./examples/solutions/{folder_name}/"
mkdir_p(relative_path)

with open(f"{relative_path}log.csv", 'x') as log:
        
        log.write("instance,initial value,final value,generation time,VND time\n")

        for instance in range(1, INSTANCES_A_TESTER + 1):
                print(f"Instance {instance}")

                # importation du problème
                problem: Problem = Importer().import_problem(f"Instance{instance}.txt")

                # génération de la solution initiale
                print("\tGénération d'une solution initiale :")
                start_time = perf_counter()
                solution: Solution = Solution.from_problem(problem)
                end_time = perf_counter()

                initial_value: int = solution.value()
                initial_time: float = end_time - start_time
                print(f"\tTemps de génération d'une solution initiale : {initial_time} s")
                print(f"Valeur de la solution initiale : {initial_value}")

                # VND   
                neighborhoods: List[Neighborhood] = [
                      TwoExchangeNeighborhood(problem),
                      DoubleExchangeNeighborhood(problem),
                      BlockExchangeNeighborhood(problem),
                      ThreeExchangeNeighborhood(problem)
                      ]
                vnd: VND = VND(problem, neighborhoods)

                start_time = perf_counter()
                solution = vnd.variable_neighborhood_descent(solution, TEMPS_MAX_PAR_INSTANCE)
                end_time = perf_counter()

                vnd_value: int = solution.value()
                vnd_time: float = end_time - start_time
                print(f"\tTemps d'exécution du VND : {vnd_time} s")
                solution.cpu_time = vnd_time

                # export de la solution
                s2f = Solution2file(problem, solution, info_provider(solution))
                s2f.generate_rosterFile(relative_path)

                # log
                log.write(f"Instance{instance},{initial_value},{vnd_value},{initial_time},{vnd_time}\n")

                print(f"\tSolution exportée dans le répertoire {relative_path}\n")


# problem = Importer().import_problem("Instance8.txt")
# print(problem)
# a = Solution.from_problem(problem)

# print(a.planning)



##### SET THE a.pathTowardsProblem: str BEFORE RUNNING ####
# infos =  info_provider(a)
# s2f = Solution2file(problem, a, infos)
# s2f.generate_rosterFile("./nurse_rostering/examples/solutions/")

# vnd = VND(problem, [TwoExchangeNeighborhood(problem)])
# start_time = perf_counter()
# b = vnd.variable_neighborhood_descent(a)
# end_time = perf_counter()

# print("ELAPSED TIME :", end_time - start_time)
# b.cpu_time = end_time - start_time

# infos = info_provider(b)
# s2f = Solution2file(problem, b, infos)
# s2f.generate_rosterFile("./nurse_rostering/examples/solutions/")
