# MultiON Challenge 2022

This repository contains submission guidelines and starter code for the MultiON Challenge 2022. For challenge overview, check [challenge webpage](http://multion-challenge.cs.sfu.ca). To participate, visit EvalAI challenge [page](https://eval.ai/web/challenges/challenge-page/1595/overview).

To receive challenge updates, please join our Google Group email list: [click here](https://groups.google.com/g/multion-challenge-2022/) to join or send an email to [multion-challenge-2022+subscribe@googlegroups.com](mailto:multion-challenge-2022+subscribe@googlegroups.com).

## Task

In MultiON, an agent is tasked with navigating to a sequence of objects. These objects are flexibly inserted into a realistic 3D environment. The task is based on the [AI Habitat](https://aihabitat.org/) and [Habitat-Matterport 3D (HM3D)](https://aihabitat.org/datasets/hm3d) scenes. 

This year the challenge has two separate tracks. 
- CYLINDER Track: Each episode contains 5 target objects randomly sampled from a set of 8 cylinders with identical shapes but different colors.

- REAL-OBJECTS Track: Each episode contains 5 target objects randomly sampled from a set of 8 realistic looking 3D objects.

Additionally, there are some other changes from last year.

- Both the tracks contain five target objects (5ON) in contrast to three (3ON) from last year's challenge.
- The episodes contain some distractor (non-target) objects randomly scattered around the environment, to increase the difficulty of the task.

In summary, in each episode, the agent is initialized at a random starting position and orientation in an unseen environment and provided a sequence of 5 target objects randomly sampled (without replacement) from the set of 8 objects. The agent must navigate to each target object in the sequence (in the given order), avoiding distractor objects and enact the FOUND action to indicate discovery. The agent has access to an RGB-D camera and a noiseless GPS+Compass sensor. GPS+Compass sensor provides the agent's current location and orientation information relative to the start of the episode.


## Dataset
We use [Habitat-Matterport 3D (HM3D)](https://aihabitat.org/datasets/hm3d) for the challenge. Each episode contains five sequential targets and some distractor objects. For this year's challenge, we focus on the task of 5-ON or 5 object navigation with cylinder and realistic objects.

## Evaluation
We extend the evaluation protocol of [ObjectNav](https://arxiv.org/abs/2006.13171). We use two metrics to evaluate agent performance:  
**Progress**: Fraction of object goals that are successfully FOUND. This effectively measures if the agent was able to navigate to goals.  
**PPL**: Overall path length weighted by progress. This effectively measures the path efficiency of the agent. Formally, 

![PPL Formula](imgs/PPL.png "PPL Formula")

## Submission Guidelines 

To participate in the challenge, visit our [EvalAI](https://eval.ai/web/challenges/challenge-page/1595/overview) page. Participants need to upload docker containers with their agents using EvalAI. Before making your submission, you should run your container locally on the minival data split to ensure the performance metrics match with those of remote evaluation. We provide a base docker image and participants only need to edit `evaluate.py` file which implements the navigation agent. Instructions for building your docker container are provided below.


1. Install [nvidia-docker v2](https://github.com/NVIDIA/nvidia-docker) by following instructions given [here](https://github.com/nvidia/nvidia-docker/wiki/Installation-(version-2.0)).

2. Clone this repository: 
```
git clone https://github.com/3dlg-hcvc/multion-challenge.git
cd multion-challenge
```
3. Edit `evaluate.py` to implement your agent. Currently, it uses an agent taking random actions.

4. Make changes in the the provided Dockerfile corresponding to each track if your agent has additional dependencies. They should be installed inside a conda environment named `habitat` that already exists in our docker. For the CYLINDER Track, use Dockerfile_cylinder_objects_track, and for REAL-OBJECTS Track, use Dockerfile_real_objects_track.

5. Build the docker container (this may need `sudo` priviliges).

    For the CYLINDER Track:
```
docker build -f Dockerfile_cylinder_objects_track -t multi_on:cyl_latest .
```
    For the REAL-OBJECTS Track:
```
docker build -f Dockerfile_real_objects_track -t multi_on:real_latest .
```
    Note that we use `configs/multinav_cyl.yaml` for the CYLINDER Track and `configs/multinav_real.yaml` for the REAL-OBJECTS Track. The two configs use `OBJECTS_TYPE` to specify the type of objects to be used and the corresponding objects path specified by `CYL_OBJECTS_PATH` and `REAL_OBJECTS_PATH` respectively.

6. Download HM3D scenes [here](https://aihabitat.org/datasets/hm3d) and place the data in: `multion-challenge/data/scene_datasets/hm3d`. 

    Download the objects for the two tracks:
```
wget -O multion_cyl_objects.zip "https://aspis.cmpt.sfu.ca/projects/multion-challenge/2022/challenge/dataset/multion_cyl_objects"
wget -O multion_real_objects.zip "https://aspis.cmpt.sfu.ca/projects/multion-challenge/2022/challenge/dataset/multion_real_objects"
```
    Extract them under `multion-challenge/data`.

    Download the dataset for different splits of the two tracks.
    
    For the CYLINDER Track:
```
wget -O 5_ON_CYL_minival.zip "https://aspis.cmpt.sfu.ca/projects/multion-challenge/2022/challenge/dataset/5_ON_CYL_minival"
wget -O 5_ON_CYL_val.zip "https://aspis.cmpt.sfu.ca/projects/multion-challenge/2022/challenge/dataset/5_ON_CYL_val"
wget -O 5_ON_CYL_train.zip "https://aspis.cmpt.sfu.ca/projects/multion-challenge/2022/challenge/dataset/5_ON_CYL_train"
```
    For the REAL-OBJECTS Track:
```
wget -O 5_ON_REAL_minival.zip "https://aspis.cmpt.sfu.ca/projects/multion-challenge/2022/challenge/dataset/5_ON_REAL_minival"
wget -O 5_ON_REAL_val.zip "https://aspis.cmpt.sfu.ca/projects/multion-challenge/2022/challenge/dataset/5_ON_REAL_val"
wget -O 5_ON_REAL_train.zip "https://aspis.cmpt.sfu.ca/projects/multion-challenge/2022/challenge/dataset/5_ON_REAL_train"
```
    Extract them and place them inside `multion-challenge/data` in the following format:

```
multion-challenge/
  data/
    scene_datasets/
      hm3d/
          ...
    multion_cyl_objects/
        ...
    multion_real_objects/
        ...
    5_ON_CYL/
        train/
            content/
                ...
            train.json.gz
        minival/
            content/
                ...
            minival.json.gz
        val/
            content/
                ...
            val.json.gz
    5_ON_REAL/
        train/
            content/
                ...
            train.json.gz
        minival/
            content/
                ...
            minival.json.gz
        val/
            content/
                ...
            val.json.gz
```

7. Test the docker container locally.
    For the CYLINDER Track:
```
./test_locally_cylinder_objects_track.sh --docker-name multi_on:cyl_latest
```
    For the REAL-OBJECTS Track:
```
./test_locally_real_objects_track.sh --docker-name multi_on:real_latest
```
    You should see an output like this:

```
2022-02-05 11:28:19,591 Initializing dataset MultiObjectNav-v1
2022-02-05 11:28:19,592 initializing sim Sim-v0
2022-02-05 11:28:25,368 Initializing task MultiObjectNav-v1
Progress: 0.0
PPL: 0.0
Success: 0.0
SPL: 0.0
```

8. Install EvalAI and submit your docker image. See detailed instructions [here](https://cli.eval.ai/).

```
# Install EvalAI Command Line Interface
pip install "evalai>=1.3.5"

# Set EvalAI account token
evalai set_token <your EvalAI participant token>

# Push docker image to EvalAI docker registry
evalai push multi_on:latest --phase <phase-name>
```


## Citing MultiON Challenge 2022
If you use the multiON framework, please consider citing the following [paper](https://arxiv.org/pdf/2012.03912.pdf):
```
@inproceedings{wani2020multion,
    title       =   {Multi-ON: Benchmarking Semantic Map Memory using Multi-Object Navigation},
    author      =   {Saim Wani and Shivansh Patel and Unnat Jain and Angel X. Chang and Manolis Savva},
    booktitle   =   {Neural Information Processing Systems (NeurIPS)},
    year        =   {2020},
    }
```

## Acknowledgements
We thank the [habitat](https://aihabitat.org/) team for building the habitat framework and providing the HM3D scenes. We also thank [EvalAI](https://eval.ai/) team who helped us host the challenge.

