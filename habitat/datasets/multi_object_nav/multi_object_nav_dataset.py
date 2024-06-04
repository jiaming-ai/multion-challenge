#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import os
from typing import Any, Dict, List, Optional, Sequence, Tuple

#from habitat.config import Config
from habitat.core.registry import registry
from habitat.datasets.pointnav.pointnav_dataset import (
    CONTENT_SCENES_PATH_FIELD,
    DEFAULT_SCENE_PATH_PREFIX,
    PointNavDatasetV1,
)
from habitat.tasks.nav.multi_object_nav_task import (
    MultiObjectGoal,
    MultiObjectGoalNavEpisode,
    ObjectDesc,
    Extras
)


@registry.register_dataset(name="MultiObjectNav-v1")
class LangMultiObjectNavDatasetV1(PointNavDatasetV1):
    r"""Class inherited from PointNavDataset that loads MultiON dataset."""
    category_to_task_category_id: Dict[str, int]
    category_to_scene_annotation_category_id: Dict[str, int]
    episodes: List[MultiObjectGoalNavEpisode] = []
    content_scenes_path: str = "{data_path}/content/{scene}.json.gz"
    goals_by_category: Dict[str, Sequence[MultiObjectGoal]]

    @staticmethod
    def dedup_goals(dataset: Dict[str, Any]) -> Dict[str, Any]:
        if len(dataset["episodes"]) == 0:
            return dataset

        goals_by_category = {}
        for i, ep in enumerate(dataset["episodes"]):
            dataset["episodes"][i]["object_category"] = ep["goals"][0][
                "object_category"
            ]
            ep = MultiObjectGoalNavEpisode(**ep)

            goals_key = ep.goals_key
            if goals_key not in goals_by_category:
                goals_by_category[goals_key] = ep.goals

            dataset["episodes"][i]["goals"] = []

        dataset["goals_by_category"] = goals_by_category

        return dataset

    # def to_json(self) -> str:
    #     for i in range(len(self.episodes)):
    #         self.episodes[i].goals = []

    #     result = DatasetFloatJSONEncoder().encode(self)

    #     for i in range(len(self.episodes)):
    #         goals = self.goals_by_category[self.episodes[i].goals_key[0]]
    #         if not isinstance(goals, list):
    #             goals = list(goals)
    #         self.episodes[i].goals = goals

    #     return result

    def __init__(self, config: Optional["DictConfig"] = None) -> None:
        self.goals_by_category = {}
        super().__init__(config)
        #scenes = self.get_scenes_to_load(config)
        #self.content_scenes_path.format(config.data_path.split('{split}')[0][:-1])
        self.episodes = list(self.episodes)

    # @staticmethod
    def deserialize_goal(self, serialized_goal: Dict[str, Any]) -> MultiObjectGoal:
        g = MultiObjectGoal(**serialized_goal, position=[None], radius=None)

        g.goal_object = [ObjectDesc(**go) for go in g.goal_object]
        #if g.view_points is not None:
         #   for vidx, view in enumerate(g.view_points):
          #      view_location = ObjectViewLocation(**view)  # type: ignore
           #     view_location.agent_state = AgentState(**view_location.agent_state)  # type: ignore
            #    g.view_points[vidx] = view_location
        for goal in g.goal_object:
            goal.navigable_points = [[float(v[0]), float(v[1]), float(v[2])] for v in goal.navigable_points][:20]
        return g

    def from_json(
        self, json_str: str, scenes_dir: Optional[str] = None
    ) -> None:
        deserialized = json.loads(json_str)
        if CONTENT_SCENES_PATH_FIELD in deserialized:
            self.content_scenes_path = deserialized[CONTENT_SCENES_PATH_FIELD]

        if "category_to_task_category_id" in deserialized:
            self.category_to_task_category_id = deserialized[
                "category_to_task_category_id"
            ]

        if "category_to_scene_annotation_category_id" in deserialized:
            self.category_to_scene_annotation_category_id = deserialized[
                "category_to_scene_annotation_category_id"
            ]

        if "category_to_mp3d_category_id" in deserialized:
            self.category_to_scene_annotation_category_id = deserialized[
                "category_to_mp3d_category_id"
            ]

        assert len(self.category_to_task_category_id) == len(
            self.category_to_scene_annotation_category_id
        )

        assert set(self.category_to_task_category_id.keys()) == set(
            self.category_to_scene_annotation_category_id.keys()
        ), "category_to_task and category_to_mp3d must have the same keys"

        if len(deserialized["episodes"]) == 0:
            return

        if "goals_by_category" not in deserialized:
            deserialized = self.dedup_goals(deserialized)

        for k, v in deserialized["goals_by_category"].items():
            if type(v) != list:
                if "goals" in v.keys():
                    self.goals_by_category[k] = [
                        self.deserialize_goal(g) for g in v["goals"]
                    ]
            else:
                self.goals_by_category[k] = [
                    self.deserialize_goal(g) for g in v
                ]

        for i, episode in enumerate(deserialized["episodes"]):
            episode['object_index'] = 0
            episode["current_goal_index"] = 0
            episode = MultiObjectGoalNavEpisode(**episode)
            episode.episode_id = str(i)

            if scenes_dir is not None:
                if episode.scene_id.startswith(DEFAULT_SCENE_PATH_PREFIX):
                    episode.scene_id = episode.scene_id[
                        len(DEFAULT_SCENE_PATH_PREFIX) :
                    ]

                episode.scene_id = os.path.join(scenes_dir, episode.scene_id)

            episode.goals = [self.deserialize_goal(ng) for ng in episode.goals]
            episode.distractors = [self.deserialize_goal(ng) for ng in episode.distractors]

            self.episodes.append(episode)