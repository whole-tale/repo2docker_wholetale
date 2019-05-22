# -*- coding: utf-8 -*-

"""Main module."""

import pkg_resources
import re
import os
import shutil
import tempfile

from repo2docker.buildpacks.docker import DockerBuildPack


class WholeTaleBuildPack(DockerBuildPack):
    def binder_path(self, path):
        """
        Locate a build file in a default dir.

        .wholetale takes precedence over default binder behaviour
        """
        if os.path.exists('.wholetale'):
            return os.path.join('binder', path)
        elif os.path.exists('binder'):
            return os.path.join('.wholetale', path)
        else:
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
        if os.path.exists(self.binder_path('apt.txt')):
            with open(self.binder_path('apt.txt')) as f:
                apt_packages = []
                for l in f:
                    package = l.partition('#')[0].strip()
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
                    'root',
                    # This apt-get install is *not* quiet, since users explicitly asked for this
                    r"""
                    apt-get -qq update && \
                    apt-get install --yes --no-install-recommends {} && \
                    apt-get -qq purge && \
                    apt-get -qq clean && \
                    rm -rf /var/lib/apt/lists/*
                    """.format(
                        ' '.join(apt_packages)
                    ),
                )

    def installR_assemble_script(self):
        installR_path = self.binder_path('install.R')
        if os.path.exists(installR_path):
            return ("${NB_USER}", "Rscript %s" % installR_path)

    def descriptionR_assemble_script(self):
        description_R = 'DESCRIPTION'
        if not self.binder_dir and os.path.exists(description_R):
            return ("${NB_USER}", 'R --quiet -e "devtools::install_local(getwd())"')

    def build(self, *args, **kwargs):
        tempdir = tempfile.mkdtemp()

        with open(os.path.join(tempdir, 'Dockerfile'), 'wb') as f:
            f.write(self.render().encode('utf-8'))

        shutil.copytree('.', os.path.join(tempdir, 'src'))

        args[-1].update({'path': tempdir})  # extra_build_kwargs
        yield from super().build(*args, **kwargs)

        shutil.rmtree(tempdir, ignore_errors=True)
