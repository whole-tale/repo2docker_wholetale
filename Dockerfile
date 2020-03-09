FROM wholetale/repo2docker:ed811283

COPY . /src
RUN python3 -m pip install /src bdbag==1.5.4
COPY repo2docker_config.py /wholetale/repo2docker_config.py

