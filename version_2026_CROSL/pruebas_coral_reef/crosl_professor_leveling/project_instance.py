#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class ProjectLevelingInstance:
    """
    Datos del problema de nivelacion para la adaptacion CRO-SL.
    """

    def __init__(
        self,
        activities,
        predecessors,
        resources,
        asignation,
        max_project_duration=None,
        force_project_duration=False,
        optimized_resource_count=0,
        optimized_resources=None,
    ):
        self.activities = activities
        self.predecessors = predecessors
        self.resources = resources
        self.asignation = asignation
        self.successors = self._build_successors()
        self.earliest_start = self._build_earliest_starts()
        self.critical_project_duration = self._build_project_duration()
        self.project_duration = self._build_allowed_project_duration(
            max_project_duration
        )
        self.force_project_duration = bool(force_project_duration)
        self.latest_start = self._build_latest_starts()
        self.optimized_resources = self._resolve_optimized_resources(
            optimized_resources,
            optimized_resource_count,
        )
        self.paths = self._build_paths()
        self.non_critical_paths = [
            path for path in self.paths
            if path["slack"] > 0
        ]

    def duration(self, activity):
        return float(self.activities[activity][0])

    def activities_ordered(self):
        return sorted(
            self.activities.keys(),
            key=lambda act: (self.earliest_start.get(act, 0.0), str(act)),
        )

    def _build_successors(self):
        successors = {act: [] for act in self.activities}
        for act, preds in self.predecessors.items():
            for pred in preds:
                successors.setdefault(pred, []).append(act)
        return successors

    def _build_earliest_starts(self):
        cache = {}

        def earliest(activity):
            if activity in cache:
                return cache[activity]

            preds = self.predecessors.get(activity, [])
            if not preds:
                cache[activity] = 0.0
            else:
                cache[activity] = max(
                    earliest(pred) + self.duration(pred)
                    for pred in preds
                )
            return cache[activity]

        for act in self.activities:
            earliest(act)
        return cache

    def _build_project_duration(self):
        if not self.activities:
            return 0.0
        return max(
            self.earliest_start[act] + self.duration(act)
            for act in self.activities
        )

    def _build_allowed_project_duration(self, max_project_duration):
        if max_project_duration is None:
            return self.critical_project_duration

        try:
            allowed_duration = float(max_project_duration)
        except (TypeError, ValueError):
            return self.critical_project_duration

        return max(self.critical_project_duration, allowed_duration)

    def _build_latest_starts(self):
        cache = {}

        def latest(activity):
            if activity in cache:
                return cache[activity]

            successors = self.successors.get(activity, [])
            duration = self.duration(activity)
            if not successors:
                cache[activity] = self.project_duration - duration
            else:
                cache[activity] = min(
                    latest(succ) - duration
                    for succ in successors
                )

            stored_value = self.activities.get(activity, [0, 0])[1]
            if float(stored_value or 0) > 0:
                cache[activity] = max(cache[activity], float(stored_value))
            return cache[activity]

        for act in self.activities:
            latest(act)
        return cache

    def _resolve_optimized_resources(self, requested_resources, requested_count):
        resources = list(self.resources)
        if not resources:
            return []

        if requested_resources:
            lookup = {str(resource).lower(): resource for resource in resources}
            selected = []
            for token in requested_resources:
                text = str(token).strip()
                resource = lookup.get(text.lower())
                if resource is None and text.isdigit():
                    index = int(text) - 1
                    if 0 <= index < len(resources):
                        resource = resources[index]
                if resource is not None and resource not in selected:
                    selected.append(resource)
            if selected:
                return selected

        try:
            count = int(requested_count)
        except (TypeError, ValueError):
            count = 0
        if count <= 0 or count >= len(resources):
            return resources

        horizon = max(1, int(self.project_duration))
        loads = {resource: [0.0] * horizon for resource in resources}
        for activity in self.activities:
            start = int(self.earliest_start.get(activity, 0.0))
            end = min(horizon, start + int(self.duration(activity)))
            for resource, amount in self.asignation.get(activity, []):
                if resource not in loads:
                    continue
                for time in range(max(0, start), end):
                    loads[resource][time] += float(amount)

        def initial_variance(resource):
            values = loads[resource]
            average = sum(values) / len(values)
            return sum((value - average) ** 2 for value in values) / len(values)

        ranked = sorted(
            resources,
            key=lambda resource: (-initial_variance(resource), str(resource)),
        )
        return ranked[:count]

    def _build_paths(self):
        sources = [
            act for act in self.activities
            if not self.predecessors.get(act)
        ]
        sinks = {
            act for act in self.activities
            if not self.successors.get(act)
        }
        paths = []

        def visit(activity, current_path):
            next_path = current_path + [activity]
            if activity in sinks:
                duration = sum(self.duration(act) for act in next_path)
                paths.append(
                    {
                        "activities": next_path,
                        "duration": duration,
                        "slack": max(0.0, self.project_duration - duration),
                    }
                )
                return

            for successor in self.successors.get(activity, []):
                visit(successor, next_path)

        for source in sources:
            visit(source, [])

        return sorted(
            paths,
            key=lambda item: (item["slack"], item["duration"], item["activities"]),
        )
