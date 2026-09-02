#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path


SUMMARY_FIELDS = [
    "instance",
    "best_config",
    "r0",
    "fb",
    "rL",
    "fa",
    "fd",
    "pd",
    "best_variance",
    "avg_variance",
    "std_variance",
    "avg_best_generation",
    "comment",
]


RANKING_FIELDS = [
    "config",
    "exclusive_wins",
    "shared_wins",
    "appearances",
    "informative_appearances",
    "win_rate",
    "avg_rank",
    "avg_best_variance",
    "avg_avg_variance",
    "avg_std_variance",
    "parameters",
]

TOLERANCE = 1e-9


def parse_args():
    parser = argparse.ArgumentParser(
        description="Resume los CSV factoriales de CRO-SL por instancia y por configuracion."
    )
    parser.add_argument(
        "results_dir",
        help=(
            "Carpeta que contiene archivos *_factorial_summary.csv. "
            "La busqueda es recursiva, por lo que puede ser la carpeta general factorial_tests."
        ),
    )
    parser.add_argument(
        "--output-prefix",
        default="global",
        help="Prefijo de los CSV de salida.",
    )
    parser.add_argument(
        "--non-recursive",
        action="store_true",
        help="Busca solo en la carpeta indicada, sin entrar en subcarpetas.",
    )
    return parser.parse_args()


def parse_number(value):
    value = str(value).strip()
    if value == "":
        return 0.0
    return float(value.replace(",", "."))


def format_number(value):
    if isinstance(value, float):
        return ("%.6f" % value).replace(".", ",")
    return value


def read_summary_file(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for row in reader:
            rows.append(row)
    return rows


def instance_from_path(path):
    name = path.name
    suffix = "_factorial_summary.csv"
    if name.endswith(suffix):
        return name[: -len(suffix)]
    return path.stem


def rank_rows(rows):
    return sorted(
        rows,
        key=lambda row: (
            parse_number(row["best_variance"]),
            parse_number(row["avg_variance"]),
            parse_number(row["std_variance"]),
            parse_number(row["avg_best_generation"]),
        ),
    )


def average_ranks(rows):
    """Assign the same average rank to configurations tied in best variance."""
    ordered = sorted(rows, key=lambda row: parse_number(row["best_variance"]))
    ranks = {}
    index = 0
    while index < len(ordered):
        end = index + 1
        value = parse_number(ordered[index]["best_variance"])
        while (
            end < len(ordered)
            and abs(parse_number(ordered[end]["best_variance"]) - value) < TOLERANCE
        ):
            end += 1
        average_rank = ((index + 1) + end) / 2.0
        for row in ordered[index:end]:
            ranks[row["config"]] = average_rank
        index = end
    return ranks


def build_comment(best_rows, winning_row):
    if len(best_rows) == 32:
        return "Todas las configuraciones empatan; instancia poco sensible."
    if len(best_rows) > 1:
        return "Varias configuraciones alcanzan la mejor varianza; se elige por media/estabilidad."
    if parse_number(winning_row["std_variance"]) == 0:
        return "Mejor configuracion y comportamiento estable en las ejecuciones."
    return "Mejor configuracion por varianza; revisar estabilidad frente a alternativas cercanas."


def write_csv(path, rows, fields):
    requested_path = path
    try:
        csvfile = open(path, "w", newline="", encoding="utf-8")
    except PermissionError:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = path.with_name("%s_%s%s" % (path.stem, timestamp, path.suffix))
        print(
            "AVISO: %s esta abierto o bloqueado; se escribira en %s."
            % (requested_path, path)
        )
        csvfile = open(path, "w", newline="", encoding="utf-8")

    with csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields, delimiter=";")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: format_number(row.get(field, "")) for field in fields})
    return path


def summarize(results_dir, output_prefix, recursive=True):
    search_root = Path(results_dir)
    pattern = "**/*_factorial_summary.csv" if recursive else "*_factorial_summary.csv"
    paths = sorted(search_root.glob(pattern))
    paths = [
        path
        for path in paths
        if not path.name.startswith(output_prefix + "_")
        and not instance_from_path(path).lower().startswith("all_instances")
        and not instance_from_path(path).lower().startswith("global")
    ]
    if not paths:
        raise FileNotFoundError("No se han encontrado archivos *_factorial_summary.csv en %s" % results_dir)

    # If an instance was executed more than once, use only its most recent summary.
    latest_by_instance = {}
    for path in paths:
        instance = instance_from_path(path)
        previous = latest_by_instance.get(instance)
        if previous is None or path.stat().st_mtime > previous.stat().st_mtime:
            latest_by_instance[instance] = path
    paths = sorted(latest_by_instance.values(), key=instance_from_path)

    instance_rows = []
    config_stats = defaultdict(
        lambda: {
            "exclusive_wins": 0,
            "shared_wins": 0,
            "appearances": 0,
            "informative_appearances": 0,
            "rank_sum": 0,
            "best_variance_sum": 0.0,
            "avg_variance_sum": 0.0,
            "std_variance_sum": 0.0,
            "parameters": "",
        }
    )

    for path in paths:
        instance = instance_from_path(path)
        rows = read_summary_file(path)
        ranked = rank_rows(rows)
        winning_row = ranked[0]
        best_value = parse_number(winning_row["best_variance"])
        worst_value = max(parse_number(row["best_variance"]) for row in rows)
        best_rows = [
            row for row in rows
            if abs(parse_number(row["best_variance"]) - best_value) < TOLERANCE
        ]
        informative = abs(worst_value - best_value) >= TOLERANCE
        all_tied = len(best_rows) == len(rows)

        instance_rows.append(
            {
                "instance": instance,
                "best_config": "TIE_ALL" if all_tied else winning_row["config"],
                "r0": "" if all_tied else winning_row["r0"],
                "fb": "" if all_tied else winning_row["fb"],
                "rL": "" if all_tied else winning_row["rL"],
                "fa": "" if all_tied else winning_row["fa"],
                "fd": "" if all_tied else winning_row["fd"],
                "pd": "" if all_tied else winning_row["pd"],
                "best_variance": parse_number(winning_row["best_variance"]),
                "avg_variance": parse_number(winning_row["avg_variance"]),
                "std_variance": parse_number(winning_row["std_variance"]),
                "avg_best_generation": parse_number(winning_row["avg_best_generation"]),
                "comment": build_comment(best_rows, winning_row),
            }
        )

        ranks = average_ranks(rows) if informative else {}
        for row in rows:
            config = row["config"]
            stats = config_stats[config]
            stats["appearances"] += 1
            stats["best_variance_sum"] += parse_number(row["best_variance"])
            stats["avg_variance_sum"] += parse_number(row["avg_variance"])
            stats["std_variance_sum"] += parse_number(row["std_variance"])
            stats["parameters"] = (
                "r0={r0}, fb={fb}, rL={rL}, fa={fa}, fd={fd}, pd={pd}".format(**row)
            )
            if informative:
                stats["informative_appearances"] += 1
                stats["rank_sum"] += ranks[config]

        if informative:
            winner_configs = [row["config"] for row in best_rows]
            win_field = "exclusive_wins" if len(winner_configs) == 1 else "shared_wins"
            for config in winner_configs:
                config_stats[config][win_field] += 1

    ranking_rows = []
    for config, stats in config_stats.items():
        appearances = stats["appearances"]
        informative_appearances = stats["informative_appearances"]
        total_wins = stats["exclusive_wins"] + stats["shared_wins"]
        ranking_rows.append(
            {
                "config": config,
                "exclusive_wins": stats["exclusive_wins"],
                "shared_wins": stats["shared_wins"],
                "appearances": appearances,
                "informative_appearances": informative_appearances,
                "win_rate": (
                    total_wins / informative_appearances
                    if informative_appearances
                    else 0.0
                ),
                "avg_rank": (
                    stats["rank_sum"] / informative_appearances
                    if informative_appearances
                    else 0.0
                ),
                "avg_best_variance": stats["best_variance_sum"] / appearances,
                "avg_avg_variance": stats["avg_variance_sum"] / appearances,
                "avg_std_variance": stats["std_variance_sum"] / appearances,
                "parameters": stats["parameters"],
            }
        )

    ranking_rows.sort(
        key=lambda row: (
            -row["exclusive_wins"],
            -row["shared_wins"],
            row["avg_rank"] if row["informative_appearances"] else float("inf"),
            row["avg_avg_variance"],
            row["avg_std_variance"],
        )
    )

    output_dir = Path(results_dir)
    instance_output = output_dir / ("%s_instance_winners.csv" % output_prefix)
    ranking_output = output_dir / ("%s_config_ranking.csv" % output_prefix)

    instance_output = write_csv(instance_output, instance_rows, SUMMARY_FIELDS)
    ranking_output = write_csv(ranking_output, ranking_rows, RANKING_FIELDS)

    informative_count = sum(
        1 for row in instance_rows
        if not row["comment"].startswith("Todas las configuraciones empatan")
    )
    print("Instancias analizadas: %d" % len(instance_rows))
    print("Instancias informativas: %d" % informative_count)
    print("Instancias con empate total: %d" % (len(instance_rows) - informative_count))
    print("Tabla por instancia: %s" % instance_output)
    print("Ranking de configuraciones: %s" % ranking_output)


def main():
    args = parse_args()
    summarize(args.results_dir, args.output_prefix, recursive=not args.non_recursive)


if __name__ == "__main__":
    main()
