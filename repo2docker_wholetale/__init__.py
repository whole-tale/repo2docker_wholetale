# -*- coding: utf-8 -*-

"""Top-level package for repo2docker-wholetale."""

from .rocker import RockerWTStackBuildPack
from .jupyter import JupyterWTStackBuildPack
from .spark import JupyterSparkWTStackBuildPack
from .openrefine import OpenRefineWTStackBuildPack
from .rkernel import RJupyterWTStackBuildPack
from .matlab import MatlabWTStackBuildPack


__author__ = """Kacper Kowalik"""
__email__ = 'xarthisius.kk@gmail.com'
__version__ = '0.0.1'
