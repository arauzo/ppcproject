#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class ProjectInstance:
    """
    Contenedor simple para una instancia de scheduling de proyectos.
    """

    def __init__(self, activities, predecessors, resources, asignation, leveling=0):
        self.activities = activities
        self.predecessors = predecessors
        self.resources = resources
        self.asignation = asignation
        self.leveling = leveling
        self.successors = self._build_successors()
        self.earliest_start = self._build_earliest_starts()
        self.project_duration = self._build_project_duration()
        self.latest_start = self._build_latest_starts()

    def n_activities(self):
        return len(self.activities)

    def n_resources(self):
        return len(self.resources)

    def duration(self, activity):
        return float(self.activities[activity][0])

    def _build_successors(self):
        successors = {act: [] for act in self.activities}
        for act, preds in self.predecessors.items():
            for pred in preds:
                successors.setdefault(pred, []).append(act)
        return successors

    def _build_earliest_starts(self):
        cache = {}

        def earliest_start(activity):
            if activity in cache:
                return cache[activity]

            preds = self.predecessors.get(activity, [])
            if not preds:
                cache[activity] = 0.0
            else:
                cache[activity] = max(
                    earliest_start(pred) + self.duration(pred)
                    for pred in preds
                )
            return cache[activity]

        for act in self.activities:
            earliest_start(act)
        return cache

    def _build_project_duration(self):
        return max(
            self.earliest_start[act] + self.duration(act)
            for act in self.activities
        ) if self.activities else 0.0

    def _build_latest_starts(self):
        cache = {}

        def latest_start(activity):
            if activity in cache:
                return cache[activity]

            successors = self.successors.get(activity, [])
            duration = self.duration(activity)
            if not successors:
                cache[activity] = self.project_duration - duration
            else:
                cache[activity] = min(
                    latest_start(succ) - duration
                    for succ in successors
                )

            activity_data = self.activities.get(activity, [])
            if len(activity_data) > 1 and float(activity_data[1] or 0) > 0:
                cache[activity] = max(cache[activity], float(activity_data[1]))
            return cache[activity]

        for act in self.activities:
            latest_start(act)
        return cache
