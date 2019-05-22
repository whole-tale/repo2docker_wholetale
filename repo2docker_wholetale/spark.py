from .jupyter import JupyterWTStackBuildPack


DOCKERFILE_TEMPLATE = r"""
FROM jupyter/pyspark-notebook:abdb27a6dfbb

# Set up user
ARG NB_USER
ARG NB_UID
ENV USER ${NB_USER}
ENV HOME /home/${NB_USER}

{% if packages -%}
RUN apt-get -qq update && \
    apt-get -qq install --yes \
       {% for package in packages -%}
       {{ package }} \
       {% endfor -%}
    > /dev/null && \
    apt-get -qq purge && \
    apt-get -qq clean && \
    rm -rf /var/lib/apt/lists/*
{% endif -%}

EXPOSE 8888

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

# Allow target path repo is cloned to be configurable
ARG REPO_DIR=${HOME}
ENV REPO_DIR ${REPO_DIR}
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

# Copy and chown stuff. This doubles the size of the repo, because
# you can't actually copy as USER, only as root! Thanks, Docker!
USER root
COPY src/ ${REPO_DIR}
RUN chown -R ${NB_USER}:users ${REPO_DIR}

{% if env -%}
# The rest of the environment
{% for item in env -%}
ENV {{item[0]}} {{item[1]}}
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
USER ${NB_USER}

{% if post_build_scripts -%}
# Make sure that postBuild scripts are marked executable before executing them
{% for s in post_build_scripts -%}
RUN chmod +x {{ s }}
RUN ./{{ s }}
{% endfor %}
{% endif -%}

# Add start script
{% if start_script is not none -%}
RUN chmod +x "{{ start_script }}"
ENV R2D_ENTRYPOINT "{{ start_script }}"
{% endif -%}

# Add entrypoint
COPY /repo2docker-entrypoint /usr/local/bin/repo2docker-entrypoint
ENTRYPOINT ["/usr/local/bin/repo2docker-entrypoint"]

# Specify the default command to run
CMD ["jupyter", "notebook", "--ip", "0.0.0.0"]

{% if appendix -%}
# Appendix:
{{ appendix }}
{% endif %}
"""


class JupyterSparkWTStackBuildPack(JupyterWTStackBuildPack):
    def __init__(self):
        super().__init__()
        self.template = DOCKERFILE_TEMPLATE

    def detect(self):
        return super().detect(buildpack="SparkBuildPack")

    def get_build_scripts(self):
        # We want to avoid doing npm config from BaseImage, and installing conda
        # from CondaBuildPack
        return []
