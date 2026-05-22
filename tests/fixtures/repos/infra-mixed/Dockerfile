FROM python:3.12-slim
WORKDIR /app
COPY . .
# Smell: runs as root, no USER directive.
CMD ["python", "-m", "shop"]
