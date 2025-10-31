# syntax=docker/dockerfile:1


FROM python:3.12-slim AS builder-env

# install uv toolkit
COPY --from=ghcr.io/astral-sh/uv:0.9.4 /uv /uvx /bin/

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-editable --extra docker


FROM builder-env AS builder

ARG VERSION
ARG REF
ARG AUTHOR

ADD . /app

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    REF=${REF:?请指定环境变量REF。} && \
    AUTHOR=${AUTHOR:?请指定环境变量AUTHOR。} && \
    about="/app/src/fxxk_xiaoyoubang/__about__.py" && \
    sed -i "s|\${author}|${AUTHOR}|" ${about} && \
    sed -i "s|\${git-commit-hash}|${REF}|" ${about} && \
    sed -i "s|\${build-timestamp}|$(date -u +'%Y-%m-%dT%H:%M:%SZ')|" ${about} && \
    uv sync --no-editable --compile-bytecode --extra docker --no-dev


FROM python:3.12-slim

ENV TZ="Asia/Shanghai" LOG="INFO"
ENV REFRESH_TIME_MIN="40"
ENV CLOCK_IN_TIME_HOUR="9" CLOCK_IN_TIME_MIN="00" CLOCK_OUT_TIME_HOUR="17" CLOCK_OUT_TIME_MIN="00"
ENV CLOCK_DISTANCE="200"
ENV DEVICE_SYSTEM="Windows"

COPY --from=builder --chown=app:app /app/.venv /app/.venv

ENV PATH="/app/.venv/bin/:${PATH}"

CMD ["xyb-docker"]

