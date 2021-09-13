import os
import json
from tempfile import mkstemp
from .jupyter import JupyterWTStackBuildPack


class StataWTStackBuildPack(JupyterWTStackBuildPack):
    """
    Setup Stata for use with a repository

    This sets up Stata, JupyterLab and the
    [stata-kernel](https://kylebarron.dev/stata_kernel)
    for a Tale with the following settings:

    * `environment.json` contains `buildpack=StataBuildPack`.

    Prerequisites:
    * Docker with buildkit support
    * `repo2docker` with the `repo2docker_wholetale` plugin
    * `stata-install:<version>` image build using the
      [stata-install](https://github.com/whole-tale/stata-install)

    For example:
    repo2docker --user-name jovyan --user-id 1000 --no-run \
            --config ./repo2docker_config.py ./path-to-repo
    """

    _wt_env = None

    def detect(self):
        return super().detect(buildpack="StataBuildPack")

    def get_path(self):
        """Adds path to STATA binaries to user's PATH.
        """
        return super().get_path() + ["/usr/local/stata/"]

    def get_build_scripts(self):
        """
        Uses Docker buildkit to mount stata-install image to
        copy pre-installed core Stata product. Also installs
        Jupyter kernel.
        """
        return super().get_build_scripts() + [
            (
                "root",
                r"""
                wget -q https://xpra.org/gpg.asc -O- | apt-key add - && \
                add-apt-repository "deb https://xpra.org/ bionic main" && \
                DEBIAN_FRONTEND=noninteractive apt-get install -y  xpra xpra-html5 && \
                mkdir -p /run/xpra && chmod 755 /run/xpra && \
                mkdir -p /run/user/${NB_UID} && chown ${NB_UID} /run/user/${NB_UID} && chmod 700 /run/user/${NB_UID}  && \
                mkdir -p /usr/local/stata
                """
            ),
            (
                "root",
                r""" --mount=type=bind,target=/stata-install,source=/usr/local/stata/,from=stata-install:{stata_version} cp -r /stata-install/* /usr/local/stata""".format(stata_version=self.wt_env.get("VERSION", "16"))
            ),
            (
                "${NB_USER}",
                r"""
                ${NB_PYTHON_PREFIX}/bin/pip install stata_kernel==1.10.5 && ${NB_PYTHON_PREFIX}/bin/python -m stata_kernel.install  
                """,
            ),
            (
                "${NB_USER}",
                r"""
                sed -i "s/stata-mp/stata/g" /home/jovyan/.stata_kernel.conf 
                """,
            ),
            (
                "root",
                r"""
                sed -i "s/tray = yes/tray = no/g" /etc/xpra/conf.d/05_features.conf
                """,
            ),
            (
                "${NB_USER}",
                r"""
                mkdir -p ${HOME}/Desktop && \
                printf "[Desktop Entry]\n\
                Version=1.0\n\
                Type=Application\n\
                Name=STATA\n\
                Comment=\n\
                Exec=xstata\n\
                Icon=/usr/local/stata/stata16.png\n\
                Path=${HOME}/work/workspace\n\
                Terminal=false\n\
                StartupNotify=false\n"\
                > ${HOME}/Desktop/STATA.desktop && \
                printf "[Desktop Entry]\n\
                Version=1.0\n\
                Type=Application\n\
                Name=Terminal\n\
                Comment=\n\
                Exec=exo-open --launch TerminalEmulator\n\
                Icon=utilities-terminal\n\
                Path=${HOME}/work/workspace\n\
                Terminal=false\n\
                StartupNotify=false\n"\
                > ${HOME}/Desktop/Terminal.desktop && \
                printf "[Desktop Entry]\n\
                Version=1.0\n\
                Type=Application\n\
                Name=Firefox\n\
                Comment=\n\
                Exec=firefox %u\n\
                Icon=firefox\n\
                Path=\n\
                Terminal=false\n\
                StartupNotify=false\n"\
                > ${HOME}/Desktop/Firefox.desktop && \
                chmod +x ${HOME}/Desktop/*.desktop
                """,
            ),
        ]


    def get_base_packages(self):
        return {
            'apt-transport-https',
            'dbus-x11',
            'gnupg',
            'libpng16-16',
            'libgtk2.0-0',
            'libtinfo5',
            'python-websockify',
            'software-properties-common',
            'wget',
            'x11-apps',
            'x11-utils',
            'xubuntu-icon-theme',
            'firefox',
            'mousepad',
            'xfce4',
            'xfonts-base',
            'xvfb',
        }.union(super().get_base_packages())

