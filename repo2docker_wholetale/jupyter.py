# -*- coding: utf-8 -*-

"""Main module."""

import json
import os

from .wholetale import WholeTaleRBuildPack


class JupyterWTStackBuildPack(WholeTaleRBuildPack):

    @property
    def wt_env(self):
        if self._wt_env is None:
            with open(self.binder_path("environment.json"), "r") as fp:
                env = json.load(fp)
            self._wt_env = dict([_.split("=") for _ in env["config"]["environment"]])
        return self._wt_env

    def detect(self, buildpack="PythonBuildPack"):
        return super().detect(buildpack=buildpack)

    def get_build_script_files(self):
        """Dict of files to be copied to the container image for use in building
        """
        files = {}
        for k, v in {
            "base/healthcheck.py": "/healthcheck.py",
            "base/jupyter_notebook_config.py": "${HOME}/.jupyter/jupyter_notebook_config.py"
        }.items():
            files[os.path.join(os.path.dirname(__file__), k)] = v

        files.update(super().get_build_script_files())
        return files

    def get_build_scripts(self):
        scripts = [
            ("root", r"""mkdir ${HOME}/work"""),
            ("root", r"""chown -R ${NB_USER}:${NB_USER} ${HOME}"""),
        ]
        return super().get_build_scripts() + scripts
