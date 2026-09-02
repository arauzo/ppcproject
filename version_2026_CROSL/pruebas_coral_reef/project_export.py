#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv


def format_number(value):
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def export_history_to_csv(history, filepath):
    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=["generation", "best_fitness", "avg_fitness", "worst_fitness"],
            delimiter=";",
        )
        writer.writeheader()
        for row in history:
            writer.writerow(
                {
                    "generation": format_number(row["generation"]),
                    "best_fitness": format_number(row["best_fitness"]),
                    "avg_fitness": format_number(row["avg_fitness"]),
                    "worst_fitness": format_number(row["worst_fitness"]),
                }
            )


def export_run_summary_to_csv(summary, filepath):
    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(["parameter", "value"])
        for key, value in summary.items():
            writer.writerow([key, format_number(value)])


def export_best_individual_to_csv(individual, filepath):
    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(["activity", "start_time"])
        values = getattr(individual, "start_times", individual.priorities)
        for act, start_time in sorted(values.items()):
            writer.writerow([act, format_number(start_time)])


def export_best_schedule_to_csv(schedule, filepath):
    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(["activity", "start", "end"])
        for act, start, end in schedule:
            writer.writerow([act, format_number(start), format_number(end)])
