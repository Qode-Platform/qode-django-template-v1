# Built by .github/workflows/deploy.yml (context ., file Dockerfile) and pushed
# to Artifact Registry. Adapted from the fleet's python stack pack.
#
# Deviations from the pack, and why:
#   - CMD names THIS repo's entrypoint instead of the pack's hardcoded
#     `uvicorn app.main:app`, which is only correct for a FastAPI repo.
#
# BASE_PATH is NOT baked in: it is per-agent and only known at run time, so the
# image serves at the host root under k8s and the agent's /direct/<id>:<port>
# run supplies its own prefix.

FROM python:3.12-slim AS build
WORKDIR /app
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
COPY requirements.txt ./
RUN python -m venv /venv \
 && /venv/bin/pip install -r requirements.txt

FROM python:3.12-slim AS runtime
ARG BUILD_ID=""
WORKDIR /app
ENV PATH=/venv/bin:$PATH PYTHONUNBUFFERED=1 PORT=8000 BUILD_ID=$BUILD_ID
RUN useradd -r -u 10001 app
COPY --from=build /venv /venv
COPY --chown=app:app . .
USER app
EXPOSE 8000
CMD ["sh", "-c", "exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT}"]
