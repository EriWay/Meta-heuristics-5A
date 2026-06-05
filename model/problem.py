from typing import List, Optional

# TODO: move logic outside of constructor

class Staff:
    
    def __init__(self, days_count: int, shift_count: int, id: str, 
                 min_worktime: int, max_worktime: int, 
                 min_consecutive_shifts: int, max_consecutive_shifts: int, 
                 min_consecutive_rest_days: int, max_worked_weekends: int):
        
        self.id: str = id
        # Jours où l'employé ne travaille pas
        self.rest_days: List[int] = []
        # Minimum de minutes travaillées
        self.min_worktime: int = min_worktime
        # Maximum de minutes travaillées
        self.max_worktime: int = max_worktime
        # Minimum de jours de travail consécutifs
        self.min_consecutive_shifts: int = min_consecutive_shifts
        # Maximum de jours de travail consécutifs
        self.max_consecutive_shifts: int = max_consecutive_shifts
        # Minimum de jours de repos consécutifs
        self.min_consecutive_rest_days: int = min_consecutive_rest_days
        # Maximum de weekends travaillés
        self.max_worked_weekends: int = max_worked_weekends
        # Pour chaque poste, le nombre de jour maximum où cet employé peut y être assigné
        self.max_shift_days: List[int] = []
        # Pour chaque jour et poste, la pénalité si l'employé n'y est pas assigné
        self.shift_wish_penalties: List[List[Optional[int]]] = [[None for _ in range(shift_count)] for _ in range(days_count)]
        # Pour chaque jour et poste, la pénalité si l'employé y est assigné
        self.shift_avoid_penalties: List[List[Optional[int]]] = [[None for _ in range(shift_count)] for _ in range(days_count)]

    def __str__(self) -> str:
        out = f"Staff {self.id} :"
        out += f"\n\tRest days : {self.rest_days}"
        out += f"\n\tMin/Max Worktime : {self.min_worktime}/{self.max_worktime}"
        out += f"\n\tMin/Max Consecutive shifts : {self.min_consecutive_shifts}/{self.max_consecutive_shifts}"
        out += f"\n\tMin Consecutive rest days : {self.min_consecutive_rest_days}"
        out += f"\n\tMax worked weekends : {self.max_worked_weekends}"
        out += f"\n\tMax shift days :"
        for i, max_shift_day in enumerate(self.max_shift_days):
            out += f"\n\t\t[{i}] : {max_shift_day}"
        out += f"\n\tShift Wish Penalties : {self.shift_wish_penalties}"
        out += f"\n\tShift Avoid Penalties : {self.shift_avoid_penalties}"
        return out

class ShiftType:
    
    def __init__(self, id: str, duration: int):
        # Chaîne de caractères identifiant le shift type
        self.id: str = id
        # Durée du shift en minutes
        self.duration: int = duration
        # Liste de ShiftTypes qui ne peuvent pas être pris après celui-ci
        # self.blocked_shift_types: list[ShiftType] = []
        self.blocked_shift_types: List[int] = []
        # Pour chaque jour, représente le nombre d'employés requis.
        self.staff_requirements: List[int] = []
        # Pour chaque jour, pénalité par employé au-dessus du nombre requis
        self.cover_above_penalties: List[int] = []
        # Pour chaque jour, pénalité par employé en-dessous du nombre requis
        self.cover_below_penalties: List[int] = []
    
    def __eq__(self, __value: object) -> bool:
        if type(__value) != ShiftType:
            return False
        else:
            return self.id == __value.id
    
    def __str__(self):
        out = f"Shift {self.id} : {self.duration} minutes\n\tBlocked shifts : "
        for blocked_shift in self.blocked_shift_types:
            out += str(blocked_shift) + ", "
        out += f"\n\tStaff requirements : {self.staff_requirements}"
        out += f"\n\tCover above penalties : {self.cover_above_penalties}"
        out += f"\n\tCover below penalties : {self.cover_below_penalties}"
        return out

class Problem:

    def __init__(self, days_count: int, path_to_problem: str):
        self.days_count: int = days_count
        self.staff: List[Staff] = []
        self.shift_types: List[ShiftType] = []
        self.path_to_problem: str = path_to_problem
    
    def shift_type_from_id(self, shift_id: str)-> Optional[ShiftType]:
        for shift_type in self.shift_types:
            if shift_type.id == shift_id:
                return shift_type
        return None

    def shift_int_from_id(self, shift_id: str)-> int:
        for i in range(len(self.shift_types)):
            if self.shift_types[i].id == shift_id:
                return i
        raise RuntimeError
    
    def staff_int_from_id(self, staff_id: str)-> int:
        for i in range(len(self.staff)):
            if self.staff[i].id == staff_id:
                return i
        raise RuntimeError
    
    def __str__(self) -> str:
        out = ""
        for i, shift_type in enumerate(self.shift_types):
            out += f"=> {shift_type}\n"
            # out += self.shift_types[i].id + " " + shift_type
        for i, staff in enumerate(self.staff):
            out += f"=> {staff}\n"
        return out