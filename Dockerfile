FROM python:3.11-alpine

LABEL maintainer="flavienchenu"
LABEL description="Jinja2 configuration builder"

# Install dependencies in a single RUN to minimize layers
# and clean up in the same layer to reduce image size
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm -rf /root/.cache/pip \
    && rm /tmp/requirements.txt \
    && find /usr/local/lib/python3.11 -name "*.pyc" -delete \
    && find /usr/local/lib/python3.11 -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Copy the build script
COPY build.py /usr/local/bin/jinja4config

# Set working directory to /workspace (where user will mount their project)
WORKDIR /workspace

# Set the entrypoint
ENTRYPOINT ["python", "/usr/local/bin/jinja4config"]

# Default command shows help
CMD ["--help"]
