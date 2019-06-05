# -*- coding: utf-8 -*-

"""Main module."""

import jinja2
import json
import os
import textwrap

from .wholetale import WholeTaleBuildPack


class OpenRefineWTStackBuildPack(WholeTaleBuildPack):

    DOCKERFILE_TEMPLATE = textwrap.dedent(
        r"""
        FROM ubuntu:xenial-20180726

        EXPOSE 3333

        WORKDIR /app

        ENV OR_VER={{version}}

        RUN apt-get update -qqy && \
          apt-get install -y wget ant openjdk-8-jdk && \
          wget https://github.com/OpenRefine/OpenRefine/archive/${OR_VER}.tar.gz && \
          tar xf ${OR_VER}.tar.gz && \
          OpenRefine-${OR_VER}/refine build && \
          rm -rf ${OR_VER}.tar.gz && \
          apt-get remove -y ant openjdk-8-jdk && \
          apt-get install -y openjdk-8-jre-headless && \
          apt autoremove -qy && \
          apt-get clean && \
          rm -rf /var/lib/apt/lists/*

        RUN useradd -m -g 100 -G 100 -u 1000 -s /bin/bash wtuser

        VOLUME /wholetale
        WORKDIR /wholetale

        RUN chown 1000:100 /wholetale
        USER wtuser

        CMD /app/OpenRefine-${OR_VER}/refine -i 0.0.0.0 -d /wholetale/workspace/openrefine
        """
    )

    def detect(self):
        if not os.path.exists(self.binder_path("environment.json")):
            return False

        with open(self.binder_path("environment.json"), "r") as fp:
            env = json.load(fp)

        try:
            return env["config"]["template"] == "openrefine.tpl"
        except (KeyError, TypeError):
            return False

    def render(self):
        t = jinja2.Template(self.DOCKERFILE_TEMPLATE)

        return t.render(version='2.8')  # TODO: fixme
