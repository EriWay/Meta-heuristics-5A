from enum import Enum
from model.problem import Problem, Staff, ShiftType
from typing import List, Dict
import os

"""
Importe un problème à partir d'un fichier .txt.
"""

class Importer:

    class Section(Enum):
        HORIZON = 1,
        SHIFTS = 2,
        STAFF = 3,
        DAYS_OFF = 4,
        SHIFT_ON_REQUESTS = 5,
        SHIFT_OFF_REQUESTS = 6,
        COVER = 7


    def import_problem(self, filename: str) -> Problem:

        current_section: Importer.Section
        problem: Problem

        # Holds shift block instructions until all shifts are registered
        held_shift_blocks: Dict[int, List[str]] = {}

        # Construire le chemin absolu basé sur la localisation de ce fichier
        base_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(base_dir, "..", "examples", "instances", filename)

        with open(filepath) as f:
            for i, line in enumerate(f):


                line = line.strip()

                if len(line) == 0:
                    if current_section == Importer.Section.SHIFTS:  # noqa: F821
                        # Save held shift blocks
                        for shift_int in held_shift_blocks.keys():
                            
                            blocked_shift_ints: List[int] = [problem.shift_int_from_id(id) for id in held_shift_blocks[shift_int]]
                            problem.shift_types[shift_int].blocked_shift_types = blocked_shift_ints

                    # print(f"[{i} EMPTY] {line}")
                elif line[0] == '#':
                    # print(f"[{i} COMMENT] {line}")
                    pass
                elif line[:7] == "SECTION":
                    current_section = Importer.Section[line[8:]]
                    # print(f"[{i} section : {current_section}] {line}")
                else: #Ligne effective
                    # print(f"[{i}] {line}")

                    tokens: List[str] = line.split(',')
                    # print(tokens)

                    match current_section:
                        case Importer.Section.HORIZON:
                            problem = Problem(int(tokens[0]), filename)
                            # print(f"nouveau problème de {problem.days_count} jours")
                        case Importer.Section.SHIFTS:
                            # Tokens
                            shift_id: str = tokens[0]
                            length: int = int(tokens[1])
                            blocked_shift_ids: List[str] = tokens[2].split('|')

                            # Create shift type with duration
                            shift: ShiftType = ShiftType(shift_id, length)
                            # Add blocked shifts
                            # if len(blocked_shift_ids[0]) > 0:
                                # for blocked_shift_id in blocked_shift_ids:
                                    # shift.blocked_shift_types.append(problem.shift_type_from_id(blocked_shift_id))
                            
                            # Add shift to problem
                            problem.shift_types.append(shift)

                            # Hold shift blocks
                            if len(blocked_shift_ids[0]) > 0:
                                held_shift_blocks[problem.shift_int_from_id(shift_id)] = blocked_shift_ids
                        case Importer.Section.STAFF:
                            # Tokens
                            staff_id: str = tokens[0]
                            max_shifts: List[List[str]] = [x.split('=') for x in tokens[1].split('|')]
                            max_total_minutes: int = int(tokens[2])
                            min_total_minutes: int = int(tokens[3])
                            max_consecutive_shifts: int = int(tokens[4])
                            min_consecutive_shifts: int = int(tokens[5])
                            min_consecutive_days_off: int = int(tokens[6])
                            max_weekends: int = int(tokens[7])

                            # Create staff
                            staff: Staff = Staff(problem.days_count, len(problem.shift_types), 
                                                 staff_id, min_total_minutes, max_total_minutes,
                                                 min_consecutive_shifts, max_consecutive_shifts,
                                                 min_consecutive_days_off, max_weekends)
                            # Add max shift days
                            for max_shift in max_shifts:
                                # shift_id: str = max_shift[0]
                                max_days: int = int(max_shift[1])
                                staff.max_shift_days.append(max_days)
                            
                            # Add staff to problem
                            problem.staff.append(staff)
                        case Importer.Section.DAYS_OFF:
                            _parse_days_off(problem, tokens)
                        case Importer.Section.SHIFT_ON_REQUESTS:
                            _parse_shifts_on_requests(problem, tokens)
                        case Importer.Section.SHIFT_OFF_REQUESTS:
                            _parse_shifts_off_requests(problem, tokens)
                        case Importer.Section.COVER:
                            _parse_cover(problem, tokens)
        return problem

def _parse_days_off(problem: Problem, tokens: List[str]) -> None:
    # Tokens
    staff_id: str = tokens[0]
    days_off: List[int] = [int(x) for x in tokens[1:]]

    # Set rest days
    staff_int: int = problem.staff_int_from_id(staff_id)
    problem.staff[staff_int].rest_days = days_off

def _parse_shifts_on_requests(problem: Problem, tokens: List[str]) -> None:
    # Tokens
    staff_id: str = tokens[0]
    shift_id: str = tokens[2]
    day: int = int(tokens[1])
    weight: int = int(tokens[3])

    # Add shift on request
    staff: Staff = problem.staff[problem.staff_int_from_id(staff_id)]
    shift_int: int = problem.shift_int_from_id(shift_id)
    staff.shift_wish_penalties[day][shift_int] = weight

def _parse_shifts_off_requests(problem: Problem, tokens: List[str]) -> None:
    # Tokens
    staff_id: str = tokens[0]
    shift_id: str = tokens[2]
    day: int = int(tokens[1])
    weight: int = int(tokens[3])

    # Add shift on request
    staff: Staff = problem.staff[problem.staff_int_from_id(staff_id)]
    shift_int: int = problem.shift_int_from_id(shift_id)
    staff.shift_avoid_penalties[day][shift_int] = weight

def _parse_cover(problem: Problem, tokens: List[str]) -> None:
    # Tokens
    # day: int = int(tokens[0])
    shift_id: str = tokens[1]
    requirement: int = int(tokens[2])
    weight_under: int = int(tokens[3])
    weight_over: int = int(tokens[4])

    # Set cover values
    shift: ShiftType = problem.shift_types[problem.shift_int_from_id(shift_id)]
    shift.staff_requirements.append(requirement)
    shift.cover_below_penalties.append(weight_under)
    shift.cover_above_penalties.append(weight_over)



if __name__ == "__main__":
    importer = Importer()
    problem = importer.import_problem("Instance3.txt")

    print(problem.days_count)
    for shift_type in problem.shift_types:
        print(shift_type)
    for staff in problem.staff:
        print(staff)