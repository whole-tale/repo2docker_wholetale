import os
import json
from .jupyter import JupyterWTStackBuildPack


class MatlabWTStackBuildPack(JupyterWTStackBuildPack):
    """
    Setup Matlab for use with a repository

    This sets up MATLAB, JupyterLab and the
    [matlab-kernel](https://github.com/Calysto/matlab_kernel
    for a Tale with the following settings:

    * `environment.json` contains `buildpack=MatlabBuildPack`.
    * `toolboxes.txt` containing a valid product string for the
       selected version.  See `installer_input.txt` from the Matlab
       install media.

    Prerequisites:
    * Docker with buildkit support
    * `repo2docker` with the `repo2docker_wholetale` plugin
    * `matlab-install:<version>` image build using the
      [matlab-install](https://github.com/whole-tale/matlab-install

    For example:
    repo2docker --user-name jovyan --user-id 1000 --no-run \
            --build-arg FILE_INSTALLATION_KEY=<your key> \
            --config ./repo2docker_config.py ./path-to-repo
    """

    _wt_env = None

    def detect(self):
        return super().detect(buildpack="MatlabBuildPack")

    def get_build_env(self):
        # MLM_LICENSE_FILE specifies the path to the license at runtime
        return super().get_build_env() + [
            ("MLM_LICENSE_FILE", "/licenses/matlab/network.lic"),
            ("BASE_URL", "/matlab"),
            ("APP_PORT", "8888")
        ]

    def get_path(self):
        """Adds path to Matlab binaries to user's PATH."""
        return super().get_path() + [
            "/usr/local/MATLAB/{}/bin".format(self.wt_env.get("VERSION", "R2020a"))
        ]

    def get_build_args(self):
        """
        Return args to be set at build time. FILE_INSTALLATION_KEY is
        required only at build time.
        """
        return super().get_build_args() + ["FILE_INSTALLATION_KEY"]

    def get_build_scripts(self):
        """
        Uses Docker builtkit to mount matlab install image to
        install MATLAB core product. Installs Python engine and
        Jupyter kernel.
        """
        return super().get_build_scripts() + [
            (
                "root",
                r"""
                wget -q https://xpra.org/gpg.asc -O- | apt-key add - && \
                add-apt-repository "deb https://xpra.org/ bionic main" && \
                DEBIAN_FRONTEND=noninteractive apt-get install -y  xpra xpra-html5
                """,
            ),
            (
                "root",
                "--mount=type=bind,target=/matlab-install,source=/matlab-install/,"
                "from=matlab-install:{matlab_version} "
                "cd /matlab-install &&  ./install -mode silent -outputFile /dev/stdout "
                "-destinationFolder /usr/local/MATLAB/{matlab_version} "
                "-licensePath /matlab-install/network.lic -agreeToLicense yes "
                "-fileInstallationKey ${{FILE_INSTALLATION_KEY}} -product.MATLAB "
                "| grep --line-buffered -v fileInstallationKey "
                "| tee /dev/stderr | grep 'End - Successful' ".format(
                    matlab_version=self.wt_env.get("VERSION", "R2020a")
                ),
            ),
            (
                "${NB_USER}",
                r"""
                ${NB_PYTHON_PREFIX}/bin/pip install matlab_kernel https://github.com/mathworks/jupyter-matlab-proxy/archive/v0.2.0.tar.gz
                """,
            ),
            (
                "root",
                r"""
                cd /usr/local/MATLAB/*/extern/engines/python && python setup.py install
                """,
            )
        ]

    def get_preassemble_scripts(self):
        """
        Introduces toolboxes.txt to specify required Matlab
        toolboxes.
        """
        scripts = []

        toolboxes_path = self.binder_path("toolboxes.txt")
        if os.path.exists(toolboxes_path):
            with open(toolboxes_path) as f:
                toolboxes = f.read().splitlines()

            toolboxes = map(lambda m: "-" + m, toolboxes)

            # This is ugly, but I couldn't think of a better way. The Matlab
            # install script outputs the secret install key and succeeds on error.
            # So, I'm grepping out the secret key and grepping for the success
            # message. The tee is there so that output isn't consumed by grep.
            scripts += [
                (
                    "root",
                    "--mount=type=bind,target=/matlab-install,source=/matlab-install/,"
                    "from=matlab-install:{matlab_version} "
                    "cd /matlab-install &&  ./install -mode silent -outputFile /dev/stdout "
                    "-destinationFolder /usr/local/MATLAB/{matlab_version} "
                    "-licensePath /matlab-install/network.lic -agreeToLicense yes "
                    "-fileInstallationKey ${{FILE_INSTALLATION_KEY}} ".format(
                        matlab_version=self.wt_env.get("VERSION", "R2020a")
                    )
                    + " ".join(toolboxes)
                    + " | grep --line-buffered -v fileInstallationKey "
                    " | tee /dev/stderr | grep 'End - Successful'",
                )
            ]

        return super().get_preassemble_scripts() + scripts

    def get_base_packages(self):
        """
        Based on:
        https://github.com/mathworks-ref-arch/matlab-dockerfile/
        """
        return {
            "apt-transport-https",
            "ca-certificates",
            "curl",
            "dbus-x11",
            "gnupg",
            "lsb-release",
            "libasound2",
            "libatk1.0-0",
            "libc6",
            "libcairo2",
            "libcap2",
            "libcomerr2",
            "libcups2",
            "libdbus-1-3",
            "libfontconfig1",
            "libgconf-2-4",
            "libgcrypt20",
            "libgdk-pixbuf2.0-0",
            "libgssapi-krb5-2",
            "libgstreamer-plugins-base1.0-0",
            "libgstreamer1.0-0",
            "libglib2.0-0",
            "libgtk2.0-0",
            "libk5crypto3",
            "libkrb5-3",
            "libnspr4",
            "libnspr4-dbg",
            "libnss3",
            "libpam0g",
            "libpango-1.0-0",
            "libpangocairo-1.0-0",
            "libpangoft2-1.0-0",
            "libselinux1",
            "libsm6",
            "libsndfile1",
            "libudev1",
            "libx11-6",
            "libx11-xcb1",
            "libxcb1",
            "libxcomposite1",
            "libxcursor1",
            "libxdamage1",
            "libxext6",
            "libxfixes3",
            "libxft2",
            "libxi6",
            "libxmu6",
            "libxrandr2",
            "libxrender1",
            "libxslt1.1",
            "libxss1",
            "libxt6",
            "libxtst6",
            "libxxf86vm1",
            "procps",
            "python3-pip",
            "python-websockify",
            "software-properties-common",
            "wget",
            "xfonts-base",
            "xkb-data",
            "xvfb",
            "x11-apps",
            "x11-utils",
            "x11vnc",
            "xvfb",
            "sudo",
            "zlib1g",
            "locales",
            "locales-all",
            "gcc",
            "g++",
            "gfortran",
            "csh",
        }.union(super().get_base_packages())
