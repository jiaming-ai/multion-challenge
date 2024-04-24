FROM soniaraychau/multion-challenge:starter_v2

ENV TRACK_CONFIG_FILE "/multion-chal-starter/configs/multinav.yaml"

# RUN /bin/bash -c "conda remove --name habitat --yes"

RUN /bin/bash -c "conda create -n habitat python=3.9 cmake=3.14.0 --yes"
# RUN /bin/bash -c "conda init bash"

# RUN /bin/bash -c ". activate habitat; python -m pip uninstall habitat_sim --yes; python -m pip uninstall habitat --yes"
# RUN /bin/bash -c "rm -rf habitat-sim; rm -rf habitat-lab"

SHELL ["conda", "run", "-n", "habitat", "/bin/bash", "-c"]

# Setup habitat-sim
# RUN /bin/bash -c "conda activate habitat; conda install habitat-sim==0.2.2 headless -c conda-forge -c aihabitat --yes"

# Silence habitat-sim logs
ENV GLOG_minloglevel=2
ENV HABITAT_SIM_LOG="quiet"
ENV MAGNUM_LOG="quiet"
RUN /bin/bash -c "conda activate habitat; conda install habitat-sim==0.2.5 headless -c conda-forge -c aihabitat --yes"

RUN /bin/bash -c "pip install yacs gym opencv-python omegaconf"
# Install habitat-lab
#RUN /bin/bash -c "git clone --branch v0.2.5 https://github.com/facebookresearch/habitat-lab.git"
# RUN /bin/bash -c "conda activate habitat; cd habitat-lab; python -m pip install -e ."
#RUN /bin/bash -c "cd habitat-lab; python -m pip install -e ."

ADD data data
ADD habitat habitat
ADD configs configs
ADD evaluate.py evaluate.py

CMD ["/bin/bash", "-c", "source activate habitat && export CHALLENGE_CONFIG_FILE=$TRACK_CONFIG_FILE && bash submit.sh"]
