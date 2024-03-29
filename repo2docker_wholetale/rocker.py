# -*- coding: utf-8 -*-

"""Main module."""

import jinja2
import json
import os
import textwrap

from distutils.version import LooseVersion as V

from .wholetale import WholeTaleBuildPack


class RockerWTStackBuildPack(WholeTaleBuildPack):

    DOCKERFILE_TEMPLATE = textwrap.dedent(
        r"""
        FROM rocker/geospatial:{{ image_spec }}
        ENV DEBIAN_FRONTEND=noninteractive

        # Buster used to be stable, but now it's not
        RUN echo 'Acquire::AllowReleaseInfoChange::Suite "true";' > /etc/apt/apt.conf.d/01allow_releaseinfo_changes && \
            echo 'Acquire::AllowReleaseInfoChange::Version "true";' >> /etc/apt/apt.conf.d/01allow_releaseinfo_changes

        # Curl used to download patched rstudio package
        RUN apt-get -qq update && \
        apt-get -qq install --yes --no-install-recommends \
            {% for package in base_packages -%}
            {{ package }} \
            {% endfor -%}
        > /dev/null && \
        apt-get -qq purge && \
        apt-get -qq clean && \
        rm -rf /var/lib/apt/lists/*

        # Use bash as default shell, rather than sh
        ENV SHELL /bin/bash

        # Set up user and repo_dir (not used in this template)
        ARG NB_USER=rstudio
        ARG NB_UID=1000
        ARG USER=rstudio
        ENV NB_USER=rstudio
        ENV NB_UID=1000
        # USER required for --auth-none 1
        ENV USER=rstudio

        EXPOSE 8787

        {% if build_env -%}
        # Environment variables required for build
        {% for item in build_env -%}
        ENV {{item[0]}} {{item[1]}}
        {% endfor -%}
        {% endif -%}

        {% if path -%}
        # Special case PATH
        ENV PATH {{ ':'.join(path) }}:${PATH}
        {% endif -%}

        {% if build_script_files -%}
        # If scripts required during build are present, copy them
        {% for src, dst in build_script_files.items() %}
        COPY {{ src }} {{ dst }}
        {% endfor -%}
        {% endif -%}

        {% for sd in build_script_directives -%}
        {{sd}}
        {% endfor %}

        ARG REPO_DIR
        ENV REPO_DIR /WholeTale/workspace
        WORKDIR ${REPO_DIR}

        # We want to allow two things:
        #   1. If there's a .local/bin directory in the repo, things there
        #      should automatically be in path
        #   2. postBuild and users should be able to install things into ~/.local/bin
        #      and have them be automatically in path
        #
        # The XDG standard suggests ~/.local/bin as the path for local user-specific
        # installs. See https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
        ENV PATH ${HOME}/.local/bin:${REPO_DIR}/.local/bin:${PATH}

        USER root
        # Copy cwd, to get aux files, it's going to be overshadowed with WT mount
        COPY src/ ${REPO_DIR}
        # Must chown for build (i.e., install.R)
        RUN chown -R ${NB_USER}:${NB_USER} ${REPO_DIR}

        {% if env -%}
        # The rest of the environment
        {% for item in env -%}
        ENV {{item[0]}}={{item[1]}}
        {% endfor -%}
        {% endif -%}

        # Run assemble scripts! These will actually build the specification
        # in the repository into the image.
        {% for sd in assemble_script_directives -%}
        {{ sd }}
        {% endfor %}

        # Container image Labels!
        # Put these at the end, since we don't want to rebuild everything
        # when these change! Did I mention I hate Dockerfile cache semantics?
        {% for k, v in labels.items() %}
        LABEL {{k}}="{{v}}"
        {%- endfor %}

        # We always want containers to run as non-root
        USER rstudio

        {% if post_build_scripts -%}
        # Make sure that postBuild scripts are marked executable before executing them
        {% for s in post_build_scripts -%}
        RUN chmod +x {{ s }}
        RUN ./{{ s }}
        {% endfor %}
        {% endif -%}

        # Add start script
        {% if files["start"] -%}
        RUN chmod +x "{{ files["start"] }}"
        ENTRYPOINT ["{{ files["start"] }}"]
        {% endif -%}

        # Add healtcheck script
        #HEALTHCHECK --interval=5s --timeout=15s --start-period=5s CMD python3 /healthcheck.py 8888

        {% if appendix -%}
        # Appendix:
        {{ appendix }}
        {% endif %}
        """
    )

    def detect(self):
        if not os.path.exists(self.binder_path("environment.json")):
            return False

        with open(self.binder_path("environment.json"), "r") as fp:
            env = json.load(fp)

        try:
            return env["config"]["buildpack"] == "RockerBuildPack"
        except (KeyError, TypeError):
            return False

    def get_build_scripts(self):
        rstudio_url = self.wt_env.get(
            "WT_RSTUDIO_URL",
            (
                "https://github.com/whole-tale/rstudio/releases/download/"
                "v1.4.1106-wt/rstudio-server-1.4.1106-bionic-amd64.deb"
            ),
        )
        rstudio_checksum = self.wt_env.get(
            "WT_RSTUDIO_MD5", "1d2bbd588f9a3ac00580939d4812a7d1"
        )

        scripts = [
            (
                "root",
                r"""
                mkdir /WholeTale && \
                chown rstudio:rstudio /WholeTale
                """,
            ),
            (
                "root",
                # Install RStudio!
                r"""
                curl --silent --location --fail {rstudio_url} > /tmp/rstudio.deb && \
                echo '{rstudio_checksum} /tmp/rstudio.deb' | md5sum -c - && \
                dpkg -i /tmp/rstudio.deb && \
                rm /tmp/rstudio.deb && \
                chown -R rstudio:rstudio /var/lib/rstudio-server
                """.format(
                    rstudio_url=rstudio_url, rstudio_checksum=rstudio_checksum
                ),
            ),
            (
                "root",
                # Change ownership of rserver config
                r"""
                chown -R rstudio:rstudio /etc/rstudio
                """,
            ),
        ]

        return super().get_build_scripts() + scripts

    def get_env(self):
        return super().get_env() + [('PASSWORD', 'thispasswordisnotusedanywhere')]

    def get_build_script_files(self):
        """Dict of files to be copied to the container image for use in building
        """
        files = {os.path.join(os.path.dirname(__file__), "r/start.sh"): "/start.sh"}
        files.update(super().get_build_script_files())
        return files

    def get_assemble_scripts(self):
        assemble_scripts = [
            assemble_script
            for assemble_script in (
                self.apt_assemble_script(),
                self.installR_assemble_script(),
                self.descriptionR_assemble_script(),
            )
            if assemble_script is not None
        ]
        return super().get_assemble_scripts() + assemble_scripts

    def get_packages(self):
        packages = ["curl"]
        if V(self.wt_env.get("WT_ROCKER_VER", "3.5.1")) <= V("3.5.3"):
            packages.append("libclang-dev")
        return packages

    def get_path(self):
        """
        Return paths to be added to the PATH environment variable.

        The RStudio package installs its binaries in a non-standard path,
        so we explicitly add that path to PATH.
        """
        return super().get_path() + ['/usr/lib/rstudio-server/bin/']

    def render(self, build_args=None):

        postbuild_file = start_file = None
        files = {'postBuild': None, 'start': None}

        for filename in files:
            if os.path.exists(self.binder_path(filename)):
                files[filename] = self.binder_path(filename)

        t = jinja2.Template(RockerWTStackBuildPack.DOCKERFILE_TEMPLATE)

        build_script_directives = []
        last_user = 'root'
        for user, script in self.get_build_scripts():
            if last_user != user:
                build_script_directives.append("USER {}".format(user))
                last_user = user
            build_script_directives.append(
                "RUN {}".format(textwrap.dedent(script.strip('\n')))
            )

        assemble_script_directives = []
        last_user = 'root'
        for user, script in self.get_assemble_scripts():
            if last_user != user:
                assemble_script_directives.append("USER {}".format(user))
                last_user = user
            assemble_script_directives.append(
                "RUN {}".format(textwrap.dedent(script.strip('\n')))
            )

        build_script_files = {
            self.generate_build_context_filename(k)[0]: v
            for k, v in self.get_build_script_files().items()
        }

        return t.render(
            image_spec=self.wt_env.get("WT_ROCKER_VER", "3.5.1"),
            files=files,
            labels={},
            path=self.get_path(),
            env=self.get_env(),
            base_packages=self.get_packages(),
            assemble_script_directives=assemble_script_directives,
            build_script_files=build_script_files,
            build_scripts=self.get_build_scripts(),
            build_script_directives=build_script_directives,
            post_build_scripts=self.get_post_build_scripts(),
            start_script="/start.sh",
        )
