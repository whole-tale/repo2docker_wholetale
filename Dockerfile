FROM craigwillis/repo2docker:update_2022_10_0

COPY . /src
RUN python3 -m pip install /src bdbag==1.6.1
COPY repo2docker_config.py /wholetale/repo2docker_config.py
