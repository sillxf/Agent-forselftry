FROM node:22-bookworm-slim AS console
WORKDIR /build/frontend
COPY RAG/frontend/package*.json ./
RUN npm ci
COPY RAG/frontend/ ./
RUN npm run build

FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 libgomp1 && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/rag
COPY pyproject.toml ./
COPY RAG ./RAG
COPY agent ./agent
COPY --from=console /build/app/web ./RAG/app/web
RUN pip install --no-cache-dir . && useradd --uid 10001 --create-home rag && mkdir -p /data /models && chown -R rag:rag /data /models
USER rag
ENV RAG_SERVICE_DATA=/data HF_HOME=/models PYTHONUNBUFFERED=1
EXPOSE 8090
CMD ["rag-service", "serve", "--host", "0.0.0.0", "--port", "8090"]
