import argparse
import os
import sys
import xml.etree.ElementTree as ET
from typing import List, Optional

# Ajoute Infirmières à sys.path pour que les imports fonctionnent
# quel que soit le répertoire courant au moment du lancement.
_PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '2026-06-05_21-05-13', 'Instance1.solution.1720.ros'))
if _PKG_ROOT not in sys.path:
    sys.path.insert(0, _PKG_ROOT)

from file_io.importer import Importer
from model.problem import Problem


Planning = List[List[Optional[int]]]


def _load_problem(instance_txt_path: str) -> Problem:
	instance_filename = os.path.basename(instance_txt_path)
	if not instance_filename.lower().endswith(".txt"):
		raise ValueError(f"Le fichier instance doit être un .txt, reçu: {instance_txt_path}")
	# Importer ouvre le fichier via un chemin relatif depuis nurse_rostering_git,
	# donc on change temporairement de répertoire.
	original_cwd = os.getcwd()
	try:
		os.chdir(_PKG_ROOT)
		return Importer().import_problem(instance_filename)
	finally:
		os.chdir(original_cwd)


def _parse_solution_ros(solution_ros_path: str, problem: Problem) -> Planning:
	if not os.path.exists(solution_ros_path):
		raise FileNotFoundError(f"Fichier solution introuvable: {solution_ros_path}")

	tree = ET.parse(solution_ros_path)
	root = tree.getroot()

	if not root.tag.endswith("Roster"):
		raise ValueError(f"Format .ros inattendu: racine '{root.tag}' (attendu: Roster)")

	planning: Planning = [
		[None for _ in range(problem.days_count)] for _ in range(len(problem.staff))
	]

	for employee in root.findall("Employee"):
		staff_id = employee.attrib.get("ID")
		if staff_id is None:
			raise ValueError("Employee sans attribut ID dans le fichier solution .ros")

		try:
			staff_int = problem.staff_int_from_id(staff_id)
		except RuntimeError as exc:
			raise ValueError(f"Infirmière inconnue dans la solution: '{staff_id}'") from exc

		for assign in employee.findall("Assign"):
			day_text = assign.findtext("Day")
			shift_id = assign.findtext("Shift")

			if day_text is None or shift_id is None:
				raise ValueError(
					f"Assign incomplet pour l'infirmière '{staff_id}' (Day/Shift manquant)"
				)

			try:
				day = int(day_text)
			except ValueError as exc:
				raise ValueError(
					f"Jour invalide '{day_text}' pour l'infirmière '{staff_id}'"
				) from exc

			if day < 0 or day >= problem.days_count:
				raise ValueError(
					f"Jour hors bornes ({day}) pour '{staff_id}', horizon={problem.days_count}"
				)

			try:
				shift_int = problem.shift_int_from_id(shift_id)
			except RuntimeError as exc:
				raise ValueError(f"Shift inconnu '{shift_id}' pour '{staff_id}'") from exc

			if planning[staff_int][day] is not None:
				raise ValueError(
					f"Affectation dupliquée pour '{staff_id}' au jour {day}"
				)

			planning[staff_int][day] = shift_int

	return planning


def _to_day_night_matrix(problem: Problem, planning: Planning) -> List[List[str]]:
	matrix: List[List[str]] = []
	for staff_idx in range(len(problem.staff)):
		row: List[str] = []
		for day in range(problem.days_count):
			shift_int = planning[staff_idx][day]
			if shift_int is None:
				row.append("-")
			else:
				shift_id = problem.shift_types[shift_int].id
				row.append("N" if shift_id == "N" else "J")
		matrix.append(row)
	return matrix


def _render_console_table(problem: Problem, matrix: List[List[str]]) -> None:
	header = ["Infirmière"] + [f"J{day}" for day in range(problem.days_count)]
	rows = [[problem.staff[i].id] + matrix[i] for i in range(len(problem.staff))]

	col_widths = [len(col) for col in header]
	for row in rows:
		for col_idx, cell in enumerate(row):
			col_widths[col_idx] = max(col_widths[col_idx], len(cell))

	def format_row(row: List[str]) -> str:
		return " | ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(row))

	print(format_row(header))
	print("-+-".join("-" * width for width in col_widths))
	for row in rows:
		print(format_row(row))


def display_assignment_table(solution_ros_path: str, instance_txt_path: str) -> None:
	problem = _load_problem(instance_txt_path)
	planning = _parse_solution_ros(solution_ros_path, problem)
	matrix = _to_day_night_matrix(problem, planning)
	_render_console_table(problem, matrix)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		description="Affiche un tableau d'affectation infirmière x jour (J/N/-) depuis un fichier .ros"
	)
	parser.add_argument("solution_ros", help="Chemin vers le fichier solution .ros")
	parser.add_argument(
		"instance_txt",
		help="Chemin vers le fichier instance .txt (ou son nom, ex: Instance2.txt)",
	)
	args = parser.parse_args()

	display_assignment_table(args.solution_ros, args.instance_txt)
