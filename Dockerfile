FROM python:3.12

WORKDIR ./bot

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

COPY ./bot/ ./bot/

ENV PYTHONPATH=/bot

CMD ["python", "./bot/main.py"]