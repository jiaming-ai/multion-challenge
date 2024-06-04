import sys
sys.path.insert(0, "")
import numpy as np
import habitat
import hydra
import os
from omegaconf import OmegaConf
os.environ["CHALLENGE_CONFIG_FILE"] = "./configs/mopa/orasem.yaml" #"./configs/multinav.yaml"

# add mc_agent path: ~/multion-challenge/mc2-agent
sys.path.insert(0, "/home/users/jiaming/multion/mc2-agent")
# print(sys.path)
from mc2.agent.mc2_agent import MC2Agent
from mc2.tasks.multion.interactive_evaluator import InteractiveEvaluator

os.environ["AGENT_EVALUATION_TYPE"] = "local"

from habitat.core.env import Env, LangMONEnv
from habitat.config.default import get_config

def main():
    config_paths = os.environ["CHALLENGE_CONFIG_FILE"]
    config_env = get_config(config_paths)
    env = LangMONEnv(config=config_env)
            
            
    agent = MC2Agent(task_config=config_env)

    evaluator = InteractiveEvaluator(config_paths="./configs/multinav.yaml")

    evaluator.play()



from multion.config.structured_configs import register_hydra_plugin
from configs.structured_configs import (
    HabitatBaselinesConfigPlugin,
)

if __name__ == "__main__":
    register_hydra_plugin(HabitatBaselinesConfigPlugin)
    main()
