import os
import json
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
        if not os.path.exists(self.binder_path("environment.json")):
            return False

        with open(self.binder_path("environment.json"), "r") as fp:
            env = json.load(fp)

        try:
            return env["config"]["buildpack"] == "StataBuildPack"
        except (KeyError, TypeError):
            return False


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
                r"""--mount=type=bind,target=/stata-install,source=/usr/local/stata/,from=stata-install:{stata_version} cp -r /stata-install /usr/local/stata""".format(stata_version=self.wt_env.get("VERSION", "16"))
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
        ]

    def get_base_packages(self):
        return {
            'libpng16-16',
        }.union(super().get_base_packages())
