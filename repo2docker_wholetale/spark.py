import os
from .jupyter import JupyterWTStackBuildPack


class JupyterSparkWTStackBuildPack(JupyterWTStackBuildPack):

    def detect(self):
        return super().detect(buildpack="SparkBuildPack")

    def get_build_scripts(self):
        env_prefix = "${KERNEL_PYTHON_PREFIX}" if self.py2 else "${NB_PYTHON_PREFIX}"
        return super().get_build_scripts() + [
            (
                "root",
                r"""cd /tmp && \
    wget -q http://archive.apache.org/dist/spark/spark-${APACHE_SPARK_VERSION}/spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    echo "E8B7F9E1DEC868282CADCAD81599038A22F48FB597D44AF1B13FCC76B7DACD2A1CAF431F95E394E1227066087E3CE6C2137C4ABAF60C60076B78F959074FF2AD *spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" | sha512sum -c - && \
    tar xzf spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz -C /usr/local --owner root --group root --no-same-owner && \
    rm spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz""",
            ),
            (
                "root",
                r"""
                cd /usr/local && ln -s spark-${APACHE_SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} spark
                """,
            ),
            (
                "root",
                r"""apt-get -qqy update && \
    apt-get install --no-install-recommends -y gnupg libcurl3 && \
    apt-key add /tmp/mesos.key && \
    echo "deb http://repos.mesosphere.io/ubuntu xenial main" > /etc/apt/sources.list.d/mesosphere.list && \
    apt-get -qqy update && \
    apt-get --no-install-recommends -y install mesos=1.2\* && \
    apt-get purge -qqy && \
    rm -rf /var/lib/apt/lists/*""",
            ),
            (
                "${NB_USER}",
                r"""conda install --quiet -p {0} -y 'pyarrow' && \
    conda clean --all -f -y""".format(
                    env_prefix
                ),
            ),
        ]

    def get_build_script_files(self):
        scripts = {
            os.path.join(os.path.dirname(__file__), "mesos.key"): "/tmp/mesos.key"
        }
        scripts.update(super().get_build_script_files())
        return scripts

    def get_base_packages(self):
        return {
            'openjdk-8-jre-headless',
            'ca-certificates-java',
            'gnupg',
        }.union(super().get_base_packages())

    def get_build_env(self):
        return [
            ("APACHE_SPARK_VERSION", "2.4.3"),
            ("HADOOP_VERSION", "2.7"),
            ("SPARK_HOME", "/usr/local/spark"),
            ("MESOS_NATIVE_LIBRARY", "/usr/local/lib/libmesos.so"),
            (
                "SPARK_OPTS",
                "--driver-java-options=-Xms1024M "
                "--driver-java-options=-Xmx4096M "
                "--driver-java-options=-Dlog4j.logLevel=info",
            ),
            (
                "PYTHONPATH",
                "$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.7-src.zip",
            ),
        ] + super().get_build_env()
