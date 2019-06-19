FROM wholetale/repo2docker:latest

COPY . /src
RUN pip install /src bdbag==1.5.4
COPY repo2docker_config.py /wholetale/repo2docker_config.py

