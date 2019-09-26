# -*- coding: utf-8 -*-

"""Main module."""

import json
import os

from repo2docker.buildpacks.r import RBuildPack


class RJupyterWTStackBuildPack(RBuildPack):
    def detect(self, buildpack="RBuildPack"):
        if not os.path.exists(self.binder_path("environment.json")):
            return False

        with open(self.binder_path("environment.json"), "r") as fp:
            env = json.load(fp)

        try:
            return env["config"]["buildpack"] == buildpack
        except (KeyError, TypeError):
            return False

    def get_build_script_files(self):
        """Dict of files to be copied to the container image for use in building
        """
        files = {}
        for k, v in {
            "base/healthcheck.py": "/healthcheck.py",
            "iframes/custom.js": "/home/jovyan/.jupyter/custom/custom.js",
            "iframes/jupyter_notebook_config.py": "/home/jovyan/.jupyter/jupyter_notebook_config.py",
        }.items():
            files[os.path.join(os.path.dirname(__file__), k)] = v

        files.update(super().get_build_script_files())
        return files

    def get_build_scripts(self):
        scripts = [("root", r"""mkdir ${HOME}/work""")]
        return super().get_build_scripts() + scripts