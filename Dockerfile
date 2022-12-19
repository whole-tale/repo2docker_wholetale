FROM wholetale/repo2docker@sha256:d8f0fdf83adf278fd97059bf393c5d4d1bac98a759ff44e30af497059a5e45d3

COPY . /src
RUN python3 -m pip install /src bdbag==1.6.1
COPY repo2docker_config.py /wholetale/repo2docker_config.py
