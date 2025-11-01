FROM python:3.12-slim

WORKDIR /authentication

RUN pip install uv

COPY pyproject.toml pyproject.toml
RUN uv venv
RUN uv pip install -r pyproject.toml

COPY . .

CMD uv run alembic upgrade head; uv run python src/main.py