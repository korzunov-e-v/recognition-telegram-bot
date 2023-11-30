FROM python:3.10-slim

COPY pyproject.toml /srv
COPY poetry.lock /srv
WORKDIR /srv

RUN apt-get update && \
    apt-get -y install ffmpeg && \
    pip install poetry==1.5.0 pip-autoremove && \
    poetry config virtualenvs.create false && \
    poetry install --no-cache --no-root && \
    apt autoremove -y

EXPOSE 80
COPY src /srv/src
COPY src /srv/src
COPY .autoflake.cfg /srv
COPY .black /srv
COPY .flake8 /srv
COPY .isort.cfg /srv

CMD python3 src/srv.py
