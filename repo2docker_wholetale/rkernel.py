# -*- coding: utf-8 -*-

"""Main module."""

import json
import os

from .wholetale import WholeTaleRBuildPack


class RJupyterWTStackBuildPack(WholeTaleRBuildPack):

    def detect(self, buildpack="RBuildPack"):
        return super().detect(buildpack=buildpack)

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
