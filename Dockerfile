FROM wholetale/repo2docker:2022.02.0-61-g393ca2c

COPY . /src
RUN python3 -m pip install /src bdbag==1.6.1
COPY repo2docker_config.py /wholetale/repo2docker_config.py
