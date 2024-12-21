FROM python:3.12

RUN mkdir backend

WORKDIR /app

COPY pyproject.toml .

RUN pip install poetry
RUN poetry cache clear --all pypi
RUN poetry install -vvv

COPY . .

ENV PYTHONPATH="/app:${PYTHONPATH}"




