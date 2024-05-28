import sys
sys.path.insert(0, "")
import numpy as np
import habitat
import hydra
import os
from omegaconf import OmegaConf
os.environ["CHALLENGE_CONFIG_FILE"] = "./configs/mopa/orasem.yaml" #"./configs/multinav.yaml"

class RandomWalker(habitat.Agent):
    def __init__(self, task_config):
        #pass
        self._POSSIBLE_ACTIONS = list(task_config.habitat.task.actions)

    def reset(self):
        pass

    def act(self, observations):
        return {"action": np.random.choice(self._POSSIBLE_ACTIONS)}

def main():
    challenge = habitat.Challenge()
    print(f"env config: {OmegaConf.to_yaml(challenge.full_config)}")
    agent = RandomWalker(task_config=challenge.full_config)

    challenge.submit(agent)

from multion.config.structured_configs import register_hydra_plugin
from configs.structured_configs import (
    HabitatBaselinesConfigPlugin,
)

if __name__ == "__main__":
    register_hydra_plugin(HabitatBaselinesConfigPlugin)
    main()
