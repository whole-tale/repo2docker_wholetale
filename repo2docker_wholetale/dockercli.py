"""Docker container engine for repo2docker using docker-cli."""
import os
import subprocess
import shutil
import tarfile
import tempfile

from repo2docker.docker import DockerEngine


class DockerCLIEngine(DockerEngine):
    """Docker container engine using docker-cli, currently only for build()."""

    def build(
        self,
        *,
        buildargs=None,
        cache_from=None,
        container_limits=None,
        tag="",
        custom_context=False,
        dockerfile="",
        fileobj=None,
        path="",
        labels=None,
        **kwargs,
    ):
        """Build docker container using docker-cli with BUILDKIT."""
        build_cmd = "docker build --progress plain"

        if tag is not None:
            build_cmd = build_cmd + " --tag " + tag

        if path:
            os.chdir(path)

        if dockerfile:
            build_cmd = build_cmd + " -f " + dockerfile

        tempdir = tempfile.mkdtemp()
        if fileobj is not None:
            tar = tarfile.open(fileobj=fileobj, mode="r")
            tar.extractall(tempdir)
            tar.close()
            path = tempdir

        if buildargs is not None:
            for key, value in buildargs.items():
                build_cmd = build_cmd + " --build-arg " + key + "=" + value

        # TODO: Handle extra_build_kwargs?

        if kwargs.get("forcerm"):
            build_cmd = build_cmd + " --force-rm"

        if kwargs.get("rm"):
            build_cmd = build_cmd + " --rm"

        if container_limits is not None:
            if "memlimit" in container_limits:
                build_cmd = build_cmd + " --memory " + container_limits["memlimit"]

        if cache_from:
            build_cmd = build_cmd + " --cache-from"
            for cache in cache_from:
                build_cmd = build_cmd + " " + cache

        build_cmd = build_cmd + " " + path

        with subprocess.Popen(
            build_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            env={"DOCKER_BUILDKIT": "1", "PROGRESS_NO_TRUNC": "1"},
        ) as p:

            while True:
                line = p.stdout.readline()
                if p.poll() is not None:
                    break
                yield {"stream": line}

            rc = p.poll()
            if rc != 0:
                yield {"error": line}

        shutil.rmtree(tempdir)
