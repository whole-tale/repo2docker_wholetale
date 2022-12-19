# -*- coding: utf-8 -*-

"""Main module."""

import json
import os

from .jupyter import JupyterWTStackBuildPack


class JuliaProjectWTBuildPack(JupyterWTStackBuildPack):

    def detect(self, buildpack="JuliaProjectBuildPack"):
        return super().detect(buildpack=buildpack)
