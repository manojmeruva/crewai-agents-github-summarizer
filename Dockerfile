# --- Stage 1: build github-mcp-server and mcpcurl from source ---
FROM golang:1.25-bookworm AS mcp-builder

RUN git clone --depth 1 https://github.com/github/github-mcp-server.git /src/github-mcp-server

WORKDIR /src/github-mcp-server
RUN go build -o /out/github-mcp-server ./cmd/github-mcp-server
RUN go build -o /out/mcpcurl ./cmd/mcpcurl

# --- Stage 2: the Django + CrewAI application ---
FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=mcp-builder /out/github-mcp-server /usr/local/bin/github-mcp-server
COPY --from=mcp-builder /out/mcpcurl /usr/local/bin/mcpcurl_bin
RUN chmod +x /usr/local/bin/github-mcp-server /usr/local/bin/mcpcurl_bin

WORKDIR /app/mcp_integration

COPY mcp_integration/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY mcp_integration/ ./

# utils.py resolves mcpcurl from the current working directory (WORKDIR above)
RUN ln -s /usr/local/bin/mcpcurl_bin ./mcpcurl

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
