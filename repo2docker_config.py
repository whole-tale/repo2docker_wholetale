from repo2docker_wholetale import (
    RockerWTStackBuildPack,
    JupyterWTStackBuildPack,
    RJupyterWTStackBuildPack,
    JupyterSparkWTStackBuildPack,
    OpenRefineWTStackBuildPack,
    MatlabWTStackBuildPack,
    StataWTStackBuildPack,
)

c.Repo2Docker.buildpacks.insert(2, RockerWTStackBuildPack)
c.Repo2Docker.buildpacks.insert(2, JupyterWTStackBuildPack)
c.Repo2Docker.buildpacks.insert(2, JupyterSparkWTStackBuildPack)
c.Repo2Docker.buildpacks.insert(2, RJupyterWTStackBuildPack)
c.Repo2Docker.buildpacks.insert(2, OpenRefineWTStackBuildPack)
c.Repo2Docker.buildpacks.insert(2, MatlabWTStackBuildPack)
c.Repo2Docker.buildpacks.insert(2, StataWTStackBuildPack)
