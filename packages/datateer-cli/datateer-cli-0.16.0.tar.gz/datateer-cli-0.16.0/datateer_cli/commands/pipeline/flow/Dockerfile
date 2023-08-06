# Ensure the environment variable DEPLOY_KEY_PREFECT_LIB is set, or the build will fail
# docker build --build-arg DEPLOY_KEY_PREFECT_LIB . --tag <image>:<version>
# to update linux dependencies rather than use the cached ones, build with docker's --no-cache flag
# FROM python:3.8.3
FROM python:3.8.7-slim-buster

WORKDIR /datateer

# If this env var is set, the "meltano install" command will use this connection string
ARG MELTANO_DATABASE_URI
ARG DEPLOY_KEY_PREFECT_LIB
RUN [ -z "$DEPLOY_KEY_PREFECT_LIB" ] && echo "DEPLOY_KEY_PREFECT_LIB is required" && exit 1 || true
ENV PIPX_BIN_DIR=/opt/pipx
ENV PATH "$PATH:/opt/pipx"

RUN apt-get -yq update \
    && apt-get -yqq install ssh git gcc
RUN mkdir /opt/pipx
RUN python -m pip install --upgrade pip
RUN pip install pipx
RUN pipx install meltano==2.1.0

# add SSH private key so we can install from the private repo datateer-prefect
RUN mkdir /root/.ssh \
    && echo "${DEPLOY_KEY_PREFECT_LIB}" > /root/.ssh/id_rsa \
    && chmod 600 /root/.ssh/id_rsa \
    && touch /root/.ssh/known_hosts \
    && ssh-keyscan github.com >> /root/.ssh/known_hosts

# copy over necessary files
COPY dbt_project.yml packages.yml /datateer/
COPY .datateer /datateer/.datateer
COPY orchestration /datateer/orchestration
COPY requirements.txt /datateer/requirements.txt
RUN pip install -r requirements.txt

# these will change more regularly, so do it near the end so their cache invalidation is minimized
COPY meltano.yml /datateer/
RUN meltano install
COPY dbt /datateer/dbt


# putting this last because it seems to invalidate the build cache every time
# ENV PYTHONPATH "${{PYTHONPATH}}:/datateer"
