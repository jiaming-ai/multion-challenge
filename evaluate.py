import sys
sys.path.insert(0, "")
import numpy as np
import habitat

class RandomWalker(habitat.Agent):
    def __init__(self, task_config: habitat.Config):
        self._POSSIBLE_ACTIONS = task_config.TASK.POSSIBLE_ACTIONS

    def reset(self):
        pass

    def act(self, observations):
        return {"action": np.random.choice(self._POSSIBLE_ACTIONS)}

def main():
    
    config = habitat.get_config("./configs/multinav_real.yaml")
    agent = RandomWalker(task_config=config)
    
    challenge = habitat.Challenge()

    challenge.submit(agent)
    
if __name__ == "__main__":
    main()
