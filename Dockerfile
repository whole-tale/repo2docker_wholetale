FROM wholetale/repo2docker:v0.7rc3

COPY . /src
RUN pip install /src
COPY repo2docker_config.py /wholetale/repo2docker_config.py
