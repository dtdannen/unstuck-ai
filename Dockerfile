FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV DEBIAN_PRIORITY=high

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install \
    # UI Requirements
    xvfb \
    xterm \
    xdotool \
    scrot \
    imagemagick \
    sudo \
    mutter \
    x11vnc \
    tint2 \
    # Terminal emulator
    xfce4-terminal \
    # Python/pyenv reqs
    build-essential \
    libssl-dev  \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    curl \
    git \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev \
    # Network tools
    net-tools \
    netcat \
    # Python
    python3 \
    python3-pip \
    python3-venv && \
    apt-get clean

# Install noVNC
RUN git clone --branch v1.5.0 https://github.com/novnc/noVNC.git /opt/noVNC && \
    git clone --branch v0.12.0 https://github.com/novnc/websockify /opt/noVNC/utils/websockify && \
    ln -s /opt/noVNC/vnc.html /opt/noVNC/index.html

# Setup user
ENV USERNAME=unstuck
ENV HOME=/home/$USERNAME
RUN useradd -m -s /bin/bash -d $HOME $USERNAME
RUN echo "${USERNAME} ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
USER unstuck
WORKDIR $HOME

# Setup Python environment
RUN python3 -m venv $HOME/venv
ENV PATH="$HOME/venv/bin:$PATH"

# Install Goose
RUN curl -fsSL https://github.com/block/goose/releases/download/stable/download_cli.sh | CONFIGURE=false bash

# Copy MCP server code
COPY --chown=$USERNAME:$USERNAME mcp_server/ $HOME/mcp_server/

# Install MCP server dependencies
RUN cd $HOME/mcp_server && \
    pip install -r requirements.txt

# Copy UI scripts
COPY --chown=$USERNAME:$USERNAME ui/ $HOME/ui/
RUN chmod +x $HOME/ui/*.sh

# Copy entrypoint script
COPY --chown=$USERNAME:$USERNAME entrypoint.sh $HOME/
RUN chmod +x $HOME/entrypoint.sh

# Expose ports
EXPOSE 8000 5900 6080

# Set environment variables for display
ARG DISPLAY_NUM=1
ARG HEIGHT=768
ARG WIDTH=1024
ENV DISPLAY_NUM=$DISPLAY_NUM
ENV HEIGHT=$HEIGHT
ENV WIDTH=$WIDTH
ENV DISPLAY=:${DISPLAY_NUM}

ENTRYPOINT ["/home/unstuck/entrypoint.sh"]
