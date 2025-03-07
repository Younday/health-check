# Install uv
FROM python:3.12-alpine AS builder

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-editable

# Copy the project into the intermediate image
ADD . /app

FROM python:3.12-alpine

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

RUN apk add tzdata
RUN ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime

# Copy the environment, but not the source code
COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --from=builder --chown=app:app /app/src /app/src

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Run the application
CMD ["uv", "run", "src/main.py"]