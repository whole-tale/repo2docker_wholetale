FROM wholetale/repo2docker:latest

COPY . /src
RUN pip install /src
COPY repo2docker_config.py /wholetale/repo2docker_config.py
