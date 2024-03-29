# -*- coding: utf-8 -*-

"""Main module."""

import datetime
import json
import re
import os
import shutil
import tempfile

from repo2docker.buildpacks.base import BuildPack
from repo2docker.buildpacks.r import RBuildPack
from repo2docker.buildpacks.python import PythonBuildPack


class WholeTaleBuildPack(BuildPack):

    major_pythons = {"2": "2.7", "3": "3.8"}
    _wt_env = None

    def get_build_args(self):
        return {}

    def binder_path(self, path):
        """
        Locate a build file in a default dir.

        .wholetale takes precedence over default binder behaviour
        """
        for possible_config_dir in (".wholetale", "binder"):
            if os.path.exists(possible_config_dir):
                return os.path.join(possible_config_dir, path)
        return path

    def get_build_script_files(self):
        """
        Generate a mapping for files injected into the container.

        Dict of files to be copied to the container image for use in building.
        This is copied before the `build_scripts` & `assemble_scripts` are
        run, so can be executed from either of them.
        It's a dictionary where the key is the source file path in the host
        system, and the value is the destination file path inside the
        container image.
        """
        files = super().get_build_script_files()
        files.update(
            {
                os.path.join(
                    os.path.dirname(__file__), "base/healthcheck.py"
                ): "/healthcheck.py"
            }
        )
        return files

    def apt_assemble_script(self):
        if os.path.exists(self.binder_path("apt.txt")):
            with open(self.binder_path("apt.txt")) as f:
                apt_packages = []
                for l in f:
                    package = l.partition("#")[0].strip()
                    if not package:
                        continue
                    # Validate that this is, indeed, just a list of packages
                    # We're doing shell injection around here, gotta be careful.
                    # FIXME: Add support for specifying version numbers
                    if not re.match(r"^[a-z0-9.+-]+", package):
                        raise ValueError(
                            "Found invalid package name {} in "
                            "apt.txt".format(package)
                        )
                    apt_packages.append(package)

            if apt_packages:
                return (
                    "root",
                    # This apt-get install is *not* quiet, since users explicitly asked for this
                    r"""
                    apt-get -qq update && \
                    apt-get install --yes --no-install-recommends {} && \
                    apt-get -qq purge && \
                    apt-get -qq clean && \
                    rm -rf /var/lib/apt/lists/*
                    """.format(
                        " ".join(apt_packages)
                    ),
                )

    def installR_assemble_script(self):
        installR_path = self.binder_path("install.R")
        if os.path.exists(installR_path):
            return ("${NB_USER}", "Rscript %s" % installR_path)

    def get_post_build_scripts(self):
        post_build = self.binder_path("postBuild")
        if os.path.exists(post_build):
            return [post_build]
        return []

    def descriptionR_assemble_script(self):
        description_R = "DESCRIPTION"
        if not self.binder_dir and os.path.exists(description_R):
            return ("${NB_USER}", 'R --quiet -e "devtools::install_local(getwd())"')

    @property
    def wt_env(self):
        if self._wt_env is None:
            with open(self.binder_path("environment.json"), "r") as fp:
                env = json.load(fp)
            self._wt_env = dict([_.split("=") for _ in env["config"]["environment"]])
        return self._wt_env

    def _build(self, *args, **kwargs):
        """Not used right now...."""
        tempdir = tempfile.mkdtemp()

        with open(os.path.join(tempdir, "Dockerfile"), "wb") as f:
            f.write(self.render().encode("utf-8"))

        shutil.copytree(".", os.path.join(tempdir, "src"))

        args[-1].update({"path": tempdir})  # extra_build_kwargs
        yield from super().build(*args, **kwargs)

        shutil.rmtree(tempdir, ignore_errors=True)

    def build(
        self,
        client,
        image_spec,
        memory_limit,
        build_args,
        cache_from,
        extra_build_kwargs,
    ):
        if build_args:
            for k, v in self.get_build_args().items():
                build_args.setdefault(k, v)
        else:
            build_args = self.get_build_args()
        yield from super().build(
            client, image_spec, memory_limit, build_args, cache_from, extra_build_kwargs
        )


class WholeTaleRBuildPack(RBuildPack):

    major_pythons = {"2": "2.7", "3": "3.8"}

    def binder_path(self, path):
        """
        Locate a build file in a default dir.

        .wholetale takes precedence over default binder behaviour
        """
        for possible_config_dir in (".wholetale", "binder"):
            if os.path.exists(possible_config_dir):
                return os.path.join(possible_config_dir, path)
        return path

    def get_build_args(self):
        return {}

    @property
    def python_version(self):
        """If environment.yaml is present, use PythonBuildPack's parent (conda) python_version"""
        if self.environment_yaml:
            return super(PythonBuildPack, self).python_version
        else:
            return super(RBuildPack, self).python_version

    def set_checkpoint_date(self):
        if not self.checkpoint_date:
            # no R snapshot date set through runtime.txt so set
            # to a reasonable default -- the last month of the previous
            # quarter
            self._checkpoint_date = self.mran_date(datetime.date.today())
            self._runtime = "r-{}".format(str(self._checkpoint_date))

    def detect(self, buildpack=None):
        if not os.path.exists(self.binder_path("environment.json")):
            return False

        with open(self.binder_path("environment.json"), "r") as fp:
            env = json.load(fp)

        try:
            if env["config"]["buildpack"] == buildpack:
                self.set_checkpoint_date()
                return True
        except (KeyError, TypeError):
            return False

    def build(
        self,
        client,
        image_spec,
        memory_limit,
        build_args,
        cache_from,
        extra_build_kwargs,
    ):
        if build_args:
            for k, v in self.get_build_args().items():
                build_args.setdefault(k, v)
        else:
            build_args = self.get_build_args()
        yield from super().build(
            client, image_spec, memory_limit, build_args, cache_from, extra_build_kwargs
        )
