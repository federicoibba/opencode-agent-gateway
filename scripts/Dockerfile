# workspace-sync image: the repo mounts scripts/ and workspaces/ read-only at
# runtime, so this only needs the Python deps for the workspace_sync package.
FROM python:3.14-slim

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /scripts
