import os
from .jupyter import JupyterWTStackBuildPack


class StataWTStackBuildPack(JupyterWTStackBuildPack):
    """
    Setup Stata for use with a repository.

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
        """Add path to STATA binaries to user's PATH."""
        return super().get_path() + ["/usr/local/stata/"]

    def get_build_scripts(self):
        """
        Uses Docker buildkit to mount stata-install image.

        Copy pre-installed core Stata product. Also installs
        Jupyter kernel.
        """
        return super().get_build_scripts() + [
            (
                "root",
                r"""
                wget -q https://xpra.org/gpg.asc -O- | apt-key add - && \
                add-apt-repository "deb https://xpra.org/ bionic main" && \
                DEBIAN_FRONTEND=noninteractive apt-get install -y  xpra=4.2.3-r7-2 xpra-html5=4.5.1-r1046-1 && \
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
                "root",
                r"""
                cd /tmp && \
                wget -q https://launchpad.net/~ubuntu-security/+archive/ubuntu/ppa/+build/15108504/+files/libpng12-0_1.2.54-1ubuntu1.1_amd64.deb && \
                dpkg -i libpng12-0_1.2.54-1ubuntu1.1_amd64.deb && \
                rm -rf /tmp/libpng12-0_1.2.54-1ubuntu1.1_amd64.deb
                """  # See #28
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
            (
                "${NB_USER}",
                r"""
                mkdir -p ${HOME}/.config/xfce4/xfconf/xfce-perchannel-xml/ && \
                printf "<?xml version='1.0' encoding='UTF-8'?> \
                <channel name='xfce4-panel' version='1.0'> \
                  <property name='configver' type='int' value='2'/> \
                  <property name='panels' type='array'> \
                    <value type='int' value='1'/> \
                    <property name='panel-1' type='empty'> \
                      <property name='position' type='string' value='p=8;x=720;y=750'/> \
                      <property name='length' type='uint' value='100'/> \
                      <property name='position-locked' type='bool' value='false'/> \
                      <property name='size' type='uint' value='36'/> \
                      <property name='plugin-ids' type='array'> \
                        <value type='int' value='1'/> \
                        <value type='int' value='3'/> \
                        <value type='int' value='15'/> \
                        <value type='int' value='6'/> \
                      </property> \
                      <property name='disable-struts' type='bool' value='false'/> \
                      <property name='nrows' type='uint' value='1'/> \
                      <property name='length-adjust' type='bool' value='true'/> \
                    </property> \
                  </property> \
                  <property name='plugins' type='empty'> \
                    <property name='plugin-1' type='string' value='applicationsmenu'/> \
                    <property name='plugin-3' type='string' value='tasklist'/> \
                    <property name='plugin-15' type='string' value='separator'> \
                      <property name='expand' type='bool' value='true'/> \
                      <property name='style' type='uint' value='0'/> \
                    </property> \
                    <property name='plugin-6' type='string' value='systray'/> \
                  </property> \
                </channel>\n" \
                > ${HOME}/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml
                """,
            ),
            (
                "root",
                r"""
                mkdir -p /usr/local/stata/ado/plus && \
                mkdir -p /usr/local/stata/ado/site && \
                printf "sysdir set SITE /usr/local/stata/ado/site\n"\
                > /usr/local/stata/profile.do
                """
            ),
        ]

    def get_assemble_scripts(self):
        """
        Introduces install.do to install required STATA packages.

        Install to the SITE directory to make available in the image
        """
        scripts = []

        installdo_path = self.binder_path("install.do")
        if os.path.exists(installdo_path):
            scripts += [
                (
                    "root",
                    r"""
                    echo ${{STATA_LICENSE_ENCODED}} | base64 -d > /usr/local/stata/stata.lic && \
                    /usr/local/stata/stata 'sysdir set PLUS /usr/local/stata/ado/site' < {} && \
                    rm /usr/local/stata/stata.lic
                    """.format(installdo_path)
                )
            ]

        return super().get_assemble_scripts() + scripts

    def get_build_args(self):
        """
        Return args to be set at build time.

        STATA_LICENSE is required only at build time.
        """
        return super().get_build_args() + ["STATA_LICENSE_ENCODED"]

    def get_preassemble_script_files(self):
        files = super().get_preassemble_script_files()
        installdo_path = self.binder_path("install.do")
        if os.path.exists(installdo_path):
            files[installdo_path] = installdo_path

        return files

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
            'xfce4-goodies',
            'xfce4-panel',
            'xfonts-base',
            'xvfb',
            'xxd',
        }.union(super().get_base_packages())
