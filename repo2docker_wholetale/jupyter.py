# -*- coding: utf-8 -*-

"""Main module."""

import io
import json
import os
import pkg_resources
import tarfile
import textwrap

from repo2docker.buildpacks.base import TEMPLATE
from repo2docker.buildpacks.python import PythonBuildPack

from .wholetale import WholeTaleBuildPack


class JupyterWTStackBuildPack(PythonBuildPack):

    def detect(self, buildpack="PythonBuildPack"):
        if not os.path.exists(self.binder_path("environment.json")):
            return False

        with open(self.binder_path("environment.json"), "r") as fp:
            env = json.load(fp)

        try:
            return (
                env["config"]["buildpack"] == buildpack
            )
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
