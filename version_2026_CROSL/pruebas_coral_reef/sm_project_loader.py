#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path


def load_sm_project(filename):
    lines = Path(filename).read_text(encoding="latin-1", errors="ignore").splitlines()

    prelaciones = []
    asignaciones_raw = []
    resource_availabilities = []
    resource_names = []
    section = None

    for line in lines:
        upper_line = line.strip().upper()
        if not upper_line or upper_line.startswith("***"):
            continue

        if "PRECEDENCE RELATIONS" in upper_line:
            section = "PREL"
            continue

        if "REQUESTS/DURATIONS" in upper_line:
            section = "ASIG"
            continue

        if "RESOURCEAVAILABILITIES" in upper_line:
            section = "REC"
            continue

        parts = line.split()
        if not parts:
            continue

        if section == "PREL" and parts[0].isdigit():
            job_id = parts[0]
            successors = parts[3:]
            prelaciones.append((job_id, successors))

        elif section == "ASIG":
            lower_parts = [p.lower() for p in parts]
            if parts[0].lower() == "jobnr." and "duration" in lower_parts:
                duration_index = lower_parts.index("duration")
                resource_tokens = parts[duration_index + 1 :]
                resource_names = []
                i = 0
                while i < len(resource_tokens):
                    if resource_tokens[i].upper() == "R" and i + 1 < len(resource_tokens):
                        resource_names.append("R" + resource_tokens[i + 1])
                        i += 2
                    else:
                        resource_names.append(resource_tokens[i])
                        i += 1
                continue

            if parts[0].isdigit():
                asignaciones_raw.append(parts)

        elif section == "REC":
            if parts[0].upper() == "R":
                resource_names = []
                i = 0
                while i < len(parts):
                    if parts[i].upper() == "R" and i + 1 < len(parts):
                        resource_names.append("R" + parts[i + 1])
                        i += 2
                    else:
                        i += 1
                continue

            if parts[0].isdigit():
                resource_availabilities = parts

    successors_dict = {}
    for job_id, successors in prelaciones:
        successors_dict[str(job_id)] = [str(s) for s in successors if s.isdigit()]

    predecessors_dict = {jid: [] for jid in successors_dict.keys()}
    for jid, succs in successors_dict.items():
        for succ in succs:
            if succ in predecessors_dict:
                predecessors_dict[succ].append(jid)

    predecessors_dict = {
        act: preds
        for act, preds in predecessors_dict.items()
        if preds
    }

    resources = {}
    if resource_names and resource_availabilities:
        for idx, resource_name in enumerate(resource_names):
            if idx < len(resource_availabilities):
                resources[str(resource_name)] = float(resource_availabilities[idx])

    activities = {}
    asignation = {}
    for row in asignaciones_raw:
        act = str(row[0])
        duration = float(row[2])
        activities[act] = [duration, 0]

        consumptions = row[3:]
        for idx, amount in enumerate(consumptions):
            if idx < len(resource_names):
                amount_value = float(amount)
                if amount_value != 0:
                    asignation.setdefault(act, []).append(
                        (str(resource_names[idx]), amount_value)
                    )

    return predecessors_dict, resources, asignation, activities
