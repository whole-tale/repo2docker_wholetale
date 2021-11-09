FROM wholetale/repo2docker:v0.7-538.g4d45007

COPY . /src
RUN python3 -m pip install /src bdbag==1.6.1
COPY repo2docker_config.py /wholetale/repo2docker_config.py
