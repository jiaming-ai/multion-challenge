FROM soniaraychau/multion-challenge:starter_2024

ADD evaluate.py /multion-chal-starter
ADD submit.sh /multion-chal-starter
ADD configs /multion-chal-starter/configs

ENV TRACK_CONFIG_FILE "/multion-chal-starter/configs/multinav.yaml"

# Silence habitat-sim logs
ENV GLOG_minloglevel=2
ENV HABITAT_SIM_LOG="quiet"
ENV MAGNUM_LOG="quiet"

WORKDIR /multion-chal-starter
CMD ["/bin/bash", "-c", "source activate habitat && export CHALLENGE_CONFIG_FILE=$TRACK_CONFIG_FILE && bash submit.sh"]
