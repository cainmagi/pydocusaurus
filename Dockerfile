ARG BASE_IMAGE=python:3.14-slim
FROM $BASE_IMAGE

LABEL maintainer="Yuchen Jin <cainmagi@gmail.com>" \
      author="Yuchen Jin <cainmagi@gmail.com>" \
      description="Developer's environment for pyDocusaurus." \
      version="1.0.0"

# Set configs
# The following args are temporary but necessary during the deployment.
# Do not change them.
ARG DEBIAN_FRONTEND=noninteractive

# Force the user to be root
USER root

WORKDIR /app
COPY ./requirements /app/requirements
COPY ./tests/requirements* /app/tests/
COPY ./docker/*.txt /app/

# Install dependencies
COPY ./docker/install*.sh /app/
RUN bash /app/install.sh

COPY ./docker/post-install.* /app/
RUN bash /app/post-install.sh

# Add Project-related files
COPY ./*.* /app/
COPY ./version /app/version
COPY ./pydocusaurus /app/pydocusaurus
COPY ./tests /app/tests
COPY ./examples /app/examples
COPY ./LICENSE /app/

# Finalize
COPY ./docker/entrypoint.sh /app/

EXPOSE 3000

ENTRYPOINT ["/bin/bash", "--login", "/app/entrypoint.sh"]
CMD [""]
