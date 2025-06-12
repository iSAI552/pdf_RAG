FROM mcr.microsoft.com/devcontainers/python:3.12
ENV PYTHONUNBUFFERED=1

# Install curl and pipx
RUN sudo apt-get update && \
    sudo apt-get install -y curl pipx && \
    pipx ensurepath

# Install poppler-utils
RUN sudo apt-get install -y poppler-utils

# Install uv using pipx
RUN pipx install uv

# Optionally, remove pip upgrade step since uv will be used
# RUN pip install --upgrade pip