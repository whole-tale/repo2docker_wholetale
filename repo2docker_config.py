from repo2docker_wholetale import RockerWTStackBuildPack
from repo2docker_wholetale import JupyterWTStackBuildPack
from repo2docker_wholetale import JupyterSparkWTStackBuildPack

c.Repo2Docker.buildpacks.insert(0, RockerWTStackBuildPack)
c.Repo2Docker.buildpacks.insert(0, JupyterWTStackBuildPack)
c.Repo2Docker.buildpacks.insert(0, JupyterSparkWTStackBuildPack)
