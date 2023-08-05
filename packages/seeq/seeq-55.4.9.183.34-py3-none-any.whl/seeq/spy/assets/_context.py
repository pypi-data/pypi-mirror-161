from __future__ import annotations

from enum import Enum
from typing import Optional, Dict

import pandas as pd

from seeq.spy._status import Status


class BuildMode(Enum):
    BUILD = 'BUILD'
    BROCHURE = 'BROCHURE'


class BuildPhase:
    # This is not an Enum because we want to put strings in the Status DataFrame
    INSTANTIATING = 'Instantiating'
    BUILDING = 'Building'
    SUCCESS = 'Success'


class BuildContext:
    workbooks: dict
    objects: dict
    cache: dict
    results_dict: Dict[tuple, dict]
    push_df: Optional[pd.DataFrame]
    status: Optional[Status]
    mode: BuildMode
    phase: str
    at_least_one_thing_built_somewhere: bool

    def __init__(self, status: Status = None, mode: BuildMode = BuildMode.BUILD):
        self.workbooks = dict()
        self.objects = dict()
        self.cache = dict()
        self.results_dict = dict()
        self.push_df = None
        self.status = status
        self.mode = mode
        self.phase = BuildPhase.INSTANTIATING
        self.at_least_one_thing_built_somewhere = True

    def __repr__(self):
        return f'Mode: {self.mode}, Phase: {self.phase}, Objects: {len(self.objects)}'

    def add_results(self, results_to_add):
        if results_to_add is None:
            return

        if isinstance(results_to_add, list):
            for result_to_add in results_to_add:
                self.results_dict[
                    (result_to_add['Path'], result_to_add['Asset'], result_to_add['Name'])] = result_to_add
        else:
            self.results_dict[
                (results_to_add['Path'], results_to_add['Asset'], results_to_add['Name'])] = results_to_add

    def get_results(self):
        return list(self.results_dict.values())

    def add_object(self, object_to_add):
        path = '' if pd.isna(object_to_add['Path']) else object_to_add['Path']
        key = (path, object_to_add['Asset'], object_to_add.__class__)
        if key in self.objects:
            raise SPyInstanceAlreadyExists(self.objects[key])
        self.objects[key] = object_to_add

    def get_object(self, row, template):
        path = '' if pd.isna(row['Build Path']) else row['Build Path']
        key = (path, row['Build Asset'], template)
        return self.objects[key]


class SPyInstanceAlreadyExists(BaseException):
    def __init__(self, instance):
        self.instance = instance
