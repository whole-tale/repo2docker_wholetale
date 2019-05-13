# -*- coding: utf-8 -*-

"""Main module."""

import io
import json
import os
import pkg_resources
import tarfile
import textwrap

from repo2docker.buildpacks.base import TEMPLATE, ENTRYPOINT_FILE
from repo2docker.buildpacks.python import PythonBuildPack

from .wholetale import WholeTaleBuildPack


class JupyterWTStackBuildPack(PythonBuildPack):

    DOCKERFILE_TEMPLATE = textwrap.dedent(TEMPLATE)

    def detect(self):
        if not os.path.exists(self.binder_path("environment.json")):
            return False

        with open(self.binder_path("environment.json"), "r") as fp:
            env = json.load(fp)

        try:
            return (
                env["config"]["template"] == "base.tpl"
                and env["config"]["buildpack"] == "PythonBuildPack"
            )
        except (KeyError, TypeError):
            return False

    def get_build_script_files(self):
        """Dict of files to be copied to the container image for use in building
        """
        files = {
            "base/healthcheck.py": "/healthcheck.py",
            "iframes/custom.js": "/home/jovyan/.jupyter/custom/custom.js",
            "iframes/jupyter_notebook_config.py": "/home/jovyan/.jupyter/jupyter_notebook_config.py",
        }
        files.update(super().get_build_script_files())
        return files

    def add_files_to_docker_context(self, tar, filter=None):
        for src in sorted(self.get_build_script_files()):
            src_parts = src.split('/')
            src_path = os.path.join(os.path.dirname(__file__), *src_parts)
            if os.path.isfile(src_path):
                tar.add(src_path, src, filter=filter)
