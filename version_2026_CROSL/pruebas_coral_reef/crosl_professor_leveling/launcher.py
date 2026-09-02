#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from sm_project_loader import load_sm_project  # noqa: E402

from .crosl import ProfessorCROSLLeveling
from .project_instance import ProjectLevelingInstance
from .recommended_config import RECOMMENDED_PARAMETERS


DEFAULT_PARAMETERS = RECOMMENDED_PARAMETERS


def build_instance_from_sm(sm_path):
    predecessors, resources, asignation, activities = load_sm_project(sm_path)
    return ProjectLevelingInstance(
        activities=activities,
        predecessors=predecessors,
        resources=resources,
        asignation=asignation,
    )


def run_professor_crosl_from_sm(sm_path, parameters=None):
    params = DEFAULT_PARAMETERS.copy()
    if parameters:
        params.update(parameters)

    instance = build_instance_from_sm(sm_path)
    return ProfessorCROSLLeveling(instance, params).run()
