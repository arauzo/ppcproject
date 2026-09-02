#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import itertools
import os
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
CORAL_DIR = PROJECT_DIR / "pruebas_coral_reef"
if str(CORAL_DIR) not in sys.path:
    sys.path.insert(0, str(CORAL_DIR))

from crosl_professor_leveling.launcher import build_instance_from_sm  # noqa: E402
from crosl_professor_leveling.crosl import ProfessorCROSLLeveling  # noqa: E402
from crosl_professor_leveling.recommended_config import RECOMMENDED_PARAMETERS  # noqa: E402


PARAMETER_GRID = {
    "p_0": [0.5, 0.8],
    "f_b": [0.7, 0.9],
    "f_a": [0.1, 0.3],
    "f_d": [0.1, 0.3],
    "p_d": [0.1, 0.3],
}


SUMMARY_FIELDS = [
    "config",
    "r0",
    "fb",
    "rL",
    "fa",
    "fd",
    "pd",
    "run_1",
    "run_2",
    "run_3",
    "best_variance",
    "worst_variance",
    "avg_variance",
    "std_variance",
    "avg_best_generation",
]


DETAIL_FIELDS = [
    "instance",
    "config",
    "execution",
    "seed",
    "r0",
    "fb",
    "rL",
    "fa",
    "fd",
    "pd",
    "best_variance",
    "best_generation",
    "generations_executed",
    "execution_time_seconds",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Ejecuta el estudio factorial CRO-SL: 32 combinaciones de parametros, "
            "3 ejecuciones por combinacion, reef 8x8 y 100 generaciones."
        )
    )
    parser.add_argument(
        "instances",
        nargs="+",
        help="Una o varias instancias .sm. Puede usarse ruta completa o nombre tipo e402.sm.",
    )
    parser.add_argument(
        "--examples-dir",
        default=str(PROJECT_DIR / "examples" / "Elmaghraby"),
        help="Carpeta donde buscar instancias si se pasa solo el nombre del archivo.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_DIR / "crosl_results" / "factorial_tests"),
        help="Carpeta de salida para los CSV.",
    )
    parser.add_argument("--runs", type=int, default=3, help="Ejecuciones por combinacion.")
    parser.add_argument("--generations", type=int, default=100, help="Generaciones por ejecucion.")
    parser.add_argument("--size-n", type=int, default=8, help="Alto del arrecife.")
    parser.add_argument("--size-m", type=int, default=8, help="Ancho del arrecife.")
    parser.add_argument("--r-l", type=float, default=0.9, help="Ratio de larvas aleatorias.")
    parser.add_argument("--seed-base", type=int, default=42000, help="Semilla base reproducible.")
    return parser.parse_args()


def resolve_instance_path(instance_arg, examples_dir):
    candidate = Path(instance_arg)
    if candidate.exists():
        return candidate.resolve()

    candidate = Path(examples_dir) / instance_arg
    if candidate.exists():
        return candidate.resolve()

    raise FileNotFoundError("No se encuentra la instancia: %s" % instance_arg)


def parameter_combinations():
    keys = list(PARAMETER_GRID.keys())
    for index, values in enumerate(itertools.product(*(PARAMETER_GRID[key] for key in keys)), start=1):
        params = dict(zip(keys, values))
        params["config"] = "C%02d" % index
        yield params


def best_generation_from_history(history):
    if not history:
        return 0
    return min(history, key=lambda row: row.get("best_fitness", float("inf"))).get("generation", 0)


def csv_value(value):
    if isinstance(value, float):
        return ("%.6f" % value).replace(".", ",")
    return value


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields, delimiter=";")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: csv_value(row.get(field, "")) for field in fields})


def build_parameters(args, combo, seed):
    params = RECOMMENDED_PARAMETERS.copy()
    params.update(
        {
            "num_generations": args.generations,
            "size_n": args.size_n,
            "size_m": args.size_m,
            "r_l": args.r_l,
            "p_0": combo["p_0"],
            "f_b": combo["f_b"],
            "f_a": combo["f_a"],
            "f_d": combo["f_d"],
            "p_d": combo["p_d"],
            "seed": seed,
            "elite_file": None,
            "initialization_file": None,
        }
    )
    return params


def run_instance(instance_path, args, output_dir, combined_rows, combined_details):
    instance_name = instance_path.name
    instance = build_instance_from_sm(str(instance_path))
    summary_rows = []
    detail_rows = []
    combinations = list(parameter_combinations())

    print("\nInstancia: %s" % instance_name)
    print("Combinaciones: %d | ejecuciones por combinacion: %d" % (len(combinations), args.runs))

    for combo_index, combo in enumerate(combinations, start=1):
        run_values = []
        run_generations = []
        run_cells = {}

        print(
            "  [%02d/%02d] %s r0=%.1f fb=%.1f fa=%.1f fd=%.1f pd=%.1f"
            % (
                combo_index,
                len(combinations),
                combo["config"],
                combo["p_0"],
                combo["f_b"],
                combo["f_a"],
                combo["f_d"],
                combo["p_d"],
            )
        )

        for run_index in range(1, args.runs + 1):
            seed = args.seed_base + combo_index * 100 + run_index
            params = build_parameters(args, combo, seed)
            start = time.perf_counter()
            result = ProfessorCROSLLeveling(instance, params).run()
            elapsed = time.perf_counter() - start

            best_variance = result.get("best_fitness", 0.0)
            best_generation = best_generation_from_history(result.get("history", []))
            generations_executed = result.get("generations_executed", 0)

            run_values.append(best_variance)
            run_generations.append(best_generation)
            if run_index <= 3:
                run_cells["run_%d" % run_index] = best_variance

            detail_row = {
                "instance": instance_name,
                "config": combo["config"],
                "execution": run_index,
                "seed": seed,
                "r0": combo["p_0"],
                "fb": combo["f_b"],
                "rL": args.r_l,
                "fa": combo["f_a"],
                "fd": combo["f_d"],
                "pd": combo["p_d"],
                "best_variance": best_variance,
                "best_generation": best_generation,
                "generations_executed": generations_executed,
                "execution_time_seconds": elapsed,
            }
            detail_rows.append(detail_row)
            combined_details.append(detail_row)

        summary_row = {
            "instance": instance_name,
            "config": combo["config"],
            "r0": combo["p_0"],
            "fb": combo["f_b"],
            "rL": args.r_l,
            "fa": combo["f_a"],
            "fd": combo["f_d"],
            "pd": combo["p_d"],
            "best_variance": min(run_values),
            "worst_variance": max(run_values),
            "avg_variance": statistics.mean(run_values),
            "std_variance": statistics.pstdev(run_values) if len(run_values) > 1 else 0.0,
            "avg_best_generation": statistics.mean(run_generations) if run_generations else 0.0,
        }
        summary_row.update(run_cells)
        summary_rows.append(summary_row)
        combined_rows.append(summary_row)

    instance_stem = instance_path.stem
    summary_path = output_dir / ("%s_factorial_summary.csv" % instance_stem)
    detail_path = output_dir / ("%s_factorial_detail.csv" % instance_stem)
    write_csv(summary_path, summary_rows, SUMMARY_FIELDS)
    write_csv(detail_path, detail_rows, DETAIL_FIELDS)
    print("  Resumen generado: %s" % summary_path)
    print("  Detalle generado: %s" % detail_path)


def main():
    args = parse_args()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(args.output_dir) / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    instance_paths = [resolve_instance_path(arg, args.examples_dir) for arg in args.instances]
    combined_rows = []
    combined_details = []

    print("Estudio factorial CRO-SL")
    print("Salida: %s" % output_dir)
    print("Parametros fijos: reef=%sx%s, generaciones=%s, rL=%.2f, elite seeds=no" % (
        args.size_n,
        args.size_m,
        args.generations,
        args.r_l,
    ))

    for instance_path in instance_paths:
        run_instance(instance_path, args, output_dir, combined_rows, combined_details)

    if len(instance_paths) > 1:
        combined_summary_path = output_dir / "all_instances_factorial_summary.csv"
        combined_detail_path = output_dir / "all_instances_factorial_detail.csv"
        write_csv(combined_summary_path, combined_rows, ["instance"] + SUMMARY_FIELDS)
        write_csv(combined_detail_path, combined_details, DETAIL_FIELDS)
        print("\nResumen combinado generado: %s" % combined_summary_path)
        print("Detalle combinado generado: %s" % combined_detail_path)


if __name__ == "__main__":
    main()
