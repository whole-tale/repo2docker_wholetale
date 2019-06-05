from repo2docker_wholetale import (
    RockerWTStackBuildPack,
    JupyterWTStackBuildPack,
    JupyterSparkWTStackBuildPack,
    OpenRefineWTStackBuildPack,
)

c.Repo2Docker.buildpacks.insert(2, RockerWTStackBuildPack)
c.Repo2Docker.buildpacks.insert(2, JupyterWTStackBuildPack)
c.Repo2Docker.buildpacks.insert(2, JupyterSparkWTStackBuildPack)
c.Repo2Docker.buildpacks.insert(2, OpenRefineWTStackBuildPack)
