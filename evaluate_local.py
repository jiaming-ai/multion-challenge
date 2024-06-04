import sys
sys.path.insert(0, "")
import numpy as np
import habitat
import os


# add mc_agent path: ~/multion-challenge/mc2-agent
sys.path.insert(0, "/home/users/jiaming/multion/mc2-agent")
# print(sys.path)
from mc2.agent.mc2_agent import MC2Agent
from mc2.tasks.multion.interactive_evaluator import InteractiveEvaluator

os.environ["CHALLENGE_CONFIG_FILE"] = "./configs/multinav.yaml"
os.environ["AGENT_EVALUATION_TYPE"] = "local"

class RandomWalker(habitat.Agent):
    def __init__(self, task_config: habitat.Config):
        self._POSSIBLE_ACTIONS = task_config.TASK.POSSIBLE_ACTIONS

    def reset(self):
        pass

    def act(self, observations):
        print(f'Observations: {observations}')
        # return {"action": np.random.choice(self._POSSIBLE_ACTIONS)}
        return {"action": "FOUND"}

def main():
    
    config = habitat.get_config("./configs/multinav.yaml")
    agent = MC2Agent(task_config=config)
    
    evaluator = InteractiveEvaluator(config_paths="./configs/multinav.yaml")

    evaluator.play()

    
if __name__ == "__main__":
    main()