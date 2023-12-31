FROM python:3.9-slim as base

# Setup env
# set the locale correctly, stop Python from generating .pyc files, and enable Python tracebacks on segfaults
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1


FROM base AS python-deps

# Install pipenv and compilation dependencies
RUN pip install pipenv

# Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy


FROM base AS runtime

# Copy virtual env from python-deps stage
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Running as the root user is a security risk
# Create and switch to a new user
RUN useradd --create-home appuser
WORKDIR /home/appuser

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
COPY main.py .
# TODO: using root user for now to be able to execute main.py
# for some reason appuser doesn't have permission to run main.py when using docker on deploy instance
# USER appuser

# https://stackoverflow.com/questions/29663459/python-app-does-not-print-anything-when-running-detached-in-docker
ENV PYTHONUNBUFFERED=1
# Run the application

# hadolint ignore=DL3025
ENTRYPOINT /docker-entrypoint.sh $0 $@
CMD [ "fastapi" ]

# ENTRYPOINT ["python", "main.py"]
# default arguments that will be added to the command
# CMD ["--directory", "directory", "8000"]