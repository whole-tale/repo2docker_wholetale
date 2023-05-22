FROM wholetale/repo2docker@sha256:88fed9ca1167cf4ff0a91b73b44fa42a83aea30968193e429ce89fc2945ec9a2

COPY . /src
RUN python3 -m pip install /src bdbag==1.6.1
COPY repo2docker_config.py /wholetale/repo2docker_config.py
