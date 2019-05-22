from repo2docker_wholetale import (
    RockerWTStackBuildPack,
    JupyterWTStackBuildPack,
    JupyterSparkWTStackBuildPack,
    OpenRefineWTStackBuildPack,
)

c.Repo2Docker.buildpacks.insert(0, RockerWTStackBuildPack)
c.Repo2Docker.buildpacks.insert(0, JupyterWTStackBuildPack)
c.Repo2Docker.buildpacks.insert(0, JupyterSparkWTStackBuildPack)
c.Repo2Docker.buildpacks.insert(0, OpenRefineWTStackBuildPack)
