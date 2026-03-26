# Count tokens from inside a container by mounting your prompts:
#
#   docker build -t tokenmeter .
#   docker run --rm -v "$PWD:/w" -w /w tokenmeter count prompts/ --model gpt-4o
#
FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/jmweb-org/tokenmeter"
LABEL org.opencontainers.image.description="Count tokens and estimate cost for prompts before you send them."
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src

RUN pip install --no-cache-dir .

ENTRYPOINT ["tokenmeter"]
CMD ["--help"]
