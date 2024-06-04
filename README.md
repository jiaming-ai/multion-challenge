

# Local testing without docker

1. setup default environment
```bash
# create a new conda environment
micromamba create -p ./.venv python=3.9 cmake -y
conda activate ./.venv

# install habitat-sim
micromamba install habitat-sim=0.2.5 withbullet -c conda-forge -c aihabitat -y

pip install yacs gym==0.26.2 opencv-python omegaconf

# install habitat-lab
git clone --depth 1 --branch v0.2.5 https://github.com/facebookresearch/habitat-lab.git
cd habitat-lab
pip install -e habitat-lab


```

<!-- 
2. install extra dependencies
```bash
pip install -r requirements.txt
```

3. run the code
```bash
python evaluate.py
``` -->