#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from typing import Any, List, Optional

import attr
import numpy as np
from gym import spaces
import magnum

import random
import magnum as mn
import math

import habitat_sim
from habitat.config import Config
from habitat.core.dataset import Dataset
from habitat.core.logging import logger
from habitat.core.registry import registry
from habitat.core.simulator import AgentState, Sensor, SensorTypes, Simulator
from habitat.core.utils import not_none_validator
from habitat.tasks.nav.nav import (
    NavigationEpisode,
    NavigationGoal,
    NavigationTask,
)

import re

@attr.s(auto_attribs=True, kw_only=True)
class MultiObjectGoalNavEpisode(NavigationEpisode):
    r"""Multi ObjectGoal Navigation Episode

    :param object_category: Category of the obect
    """
    object_category: Optional[List[str]] = None
    object_index: Optional[int]
    current_goal_index: Optional[int] = 0
    distractors: List[Any] = []

    #
    scene_dataset_config: str = attr.ib(
        default="default", validator=not_none_validator
    )
    additional_obj_config_paths: List[str] = attr.ib(
        default=[], validator=not_none_validator
    )



    @property
    def goals_key(self) -> str:
        r"""The key to retrieve the goals
        """
        return [f"{os.path.basename(self.scene_id)}_{i}" for i in self.object_category]


@attr.s(auto_attribs=True)
class ObjectViewLocation:
    r"""ObjectViewLocation provides information about a position around an object goal
    usually that is navigable and the object is visible with specific agent
    configuration that episode's dataset was created.
     that is target for
    navigation. That can be specify object_id, position and object
    category. An important part for metrics calculation are view points that
     describe success area for the navigation.

    Args:
        agent_state: navigable AgentState with a position and a rotation where
        the object is visible.
        iou: an intersection of a union of the object and a rectangle in the
        center of view. This metric is used to evaluate how good is the object
        view form current position. Higher iou means better view, iou equals
        1.0 if whole object is inside of the rectangle and no pixel inside
        the rectangle belongs to anything except the object.
    """
    agent_state: AgentState
    iou: Optional[float]


@attr.s(auto_attribs=True)
class ObjectDesc:
    r"""ObjectDesc provides information about the object instance id, centroid and
    bounding box of the object. This is used to store details about the target
    objects while creating the dataset.

    Args:
        object_id: unique id of the object.
        centroid: 3D location of the centroid of the object.
        aabb: aabb of the object.
            [
                bb.back_bottom_left,
                bb.back_bottom_right,
                bb.back_top_right,
                bb.back_top_left,
                bb.front_top_left,
                bb.front_top_right,
                bb.front_bottom_right,
                bb.front_bottom_left,
            ]
        nearest_nav_point: snapped point
        navigable_points: nearest navigable points within a threshold of the snapped point
    """
    object_id: str
    centroid: List[float]
    aabb: List[List[float]]
    nearest_nav_point: List[float]
    navigable_points: Optional[List[List[float]]] = None


@attr.s(auto_attribs=True)
class Extras:
    r"""Extra information about the dataset.
    Args:
        object_name: name of the object
        object_category: object category name usually similar to scene semantic
        categories
        room_id: id of a room where object is located, can be used to retrieve
        room from the semantic scene annotation
        room_name: name of the room, where object is located
    """
    object_name: Optional[str] = None
    object_category: Optional[str] = None
    ref_object: Optional[ObjectDesc] = None
    ref_object_category: Optional[str] = None
    room_id: Optional[str] = None
    room_name: Optional[str] = None

@attr.s(auto_attribs=True, kw_only=True)
class MultiObjectGoal(NavigationGoal):
    r"""Object goal provides information about an object that is target for
    navigation. That can be specify object_id, position and object
    category. An important part for metrics calculation are view points that
     describe success area for the navigation.
    Args:
        object_id: id that can be used to retrieve object from the semantic
        scene annotation
        object_name: name of the object
        object_category: object category name usually similar to scene semantic
        categories
        room_id: id of a room where object is located, can be used to retrieve
        room from the semantic scene annotation
        room_name: name of the room, where object is located
        view_points: navigable positions around the object with specified
        proximity of the object surface used for navigation metrics calculation.
        The object is visible from these positions.
    """

    goal_object: Optional[List[ObjectDesc]]
    language_instruction: Optional[str] = None
    extras: Optional[Extras] = None
    #TODO: added
    object_category: Optional[str] = None



@registry.register_sensor
class MultiObjectGoalSensor(Sensor):
    r"""A sensor for Object Goal specification as observations which is used in
    ObjectGoal Navigation. The goal is expected to be specified by object_id or
    semantic category id.
    For the agent in simulator the forward direction is along negative-z.
    In polar coordinate format the angle returned is azimuth to the goal.
    Args:
        sim: a reference to the simulator for calculating task observations.
        config: a config for the ObjectGoalSensor sensor. Can contain field
            GOAL_SPEC that specifies which id use for goal specification,
            GOAL_SPEC_MAX_VAL the maximum object_id possible used for
            observation space definition.
        dataset: a Object Goal navigation dataset that contains dictionaries
        of categories id to text mapping.
    """

    cls_uuid: str = "multiobjectgoal"

    def __init__(
            self, sim, config, dataset: Dataset, *args: Any, **kwargs: Any
    ):
        self._sim = sim
        self._dataset = dataset
        super().__init__(config=config)

    def _get_uuid(self, *args: Any, **kwargs: Any):
        return self.cls_uuid

    def _get_sensor_type(self, *args: Any, **kwargs: Any):
        return SensorTypes.SEMANTIC

    def _get_observation_space(self, *args: Any, **kwargs: Any):
        sensor_shape = (1,)
        max_value = (self.config.GOAL_SPEC_MAX_VAL - 1,)
        if self.config.GOAL_SPEC == "CATEGORY_LABEL_TEXT":
            return spaces.Text(255)
        elif self.config.GOAL_SPEC == "TASK_CATEGORY_ID":
            max_value = max(
                self._dataset.category_to_task_category_id.values()
            )

            return spaces.Box(
                low=0, high=max_value, shape=sensor_shape, dtype=np.int64
            )

    def get_observation(
            self,
            observations,
            *args: Any,
            episode: MultiObjectGoalNavEpisode,
            **kwargs: Any,
    ) -> Optional[int]:
        if self.config.GOAL_SPEC == "CATEGORY_LABEL_TEXT":
            if len(episode.goals) == 0:
                logger.error(
                    f"No goal specified for episode {episode.episode_id}."
                )
                return None
            curr_goal_ind = (kwargs["task"].current_goal_index
                             if kwargs["task"].current_goal_index < len(episode.goals) else -1)
            if curr_goal_ind != -1 and 'action' in kwargs and kwargs['action']['action'] == 'FOUND':
                curr_goal_ind += 1
            if curr_goal_ind == len(episode.goals):
                curr_goal_ind = -1
            category_label = episode.goals[curr_goal_ind].language_instruction
            return category_label
        elif self.config.GOAL_SPEC == "TASK_CATEGORY_ID":
            if len(episode.goals) == 0:
                logger.error(
                    f"No goal specified for episode {episode.episode_id}."
                )
                return None
            category_name = [i.object_category for i in episode.goals]
            goalArray = np.array(
                [self._dataset.category_to_task_category_id[i] + 1 for i in category_name],
                dtype=np.int64,
            )
            return goalArray[kwargs["task"].current_goal_index:kwargs["task"].current_goal_index + 1]
        elif self.config.goal_spec == "OBJECT_ID":
            return np.array([episode.goals[0].object_name_id], dtype=np.int64)
        else:
            raise RuntimeError(
                "Wrong goal_spec specified for ObjectGoalSensor."
            )

@registry.register_task(name="MultiObjectNav-v1")
class MultiObjectNavigationTask(NavigationTask):
    r"""Multi-Object Navigation Task class for a task specific methods.
    Used to explicitly state a type of the task in config.
    """
    def __init__(
        self, config, sim, dataset
    ) -> None:
        super().__init__(config=config, sim=sim, dataset=dataset)
        self.current_goal_index=0
