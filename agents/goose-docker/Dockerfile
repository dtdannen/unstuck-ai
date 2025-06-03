# /agents/goose-docker/Dockerfile

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies with proper X11 and desktop components
RUN apt-get update && apt-get install -y \
    xfce4 xfce4-goodies \
    xfce4-terminal \
    tigervnc-standalone-server tigervnc-common \
    novnc websockify \
    firefox \
    python3 python3-pip \
    xauth \
    x11-xserver-utils \
    dbus-x11 \
    sudo \
    procps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create user
RUN useradd -m -s /bin/bash goose && \
    echo 'goose:password' | chpasswd && \
    usermod -aG sudo goose

# Configure sudo to not require password
RUN echo 'goose ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER goose
WORKDIR /home/goose

# Set up VNC directories
RUN mkdir -p ~/.vnc ~/.config/xfce4

# Create VNC password
RUN echo 'password' | vncpasswd -f > ~/.vnc/passwd && \
    chmod 600 ~/.vnc/passwd

# Create xstartup script using echo commands instead of heredoc
RUN echo '#!/bin/bash' > ~/.vnc/xstartup && \
    echo '# Fix for XFCE in VNC' >> ~/.vnc/xstartup && \
    echo '' >> ~/.vnc/xstartup && \
    echo '# Set up environment' >> ~/.vnc/xstartup && \
    echo 'export XKL_XMODMAP_DISABLE=1' >> ~/.vnc/xstartup && \
    echo 'export XDG_CURRENT_DESKTOP="XFCE"' >> ~/.vnc/xstartup && \
    echo 'export XDG_MENU_PREFIX="xfce-"' >> ~/.vnc/xstartup && \
    echo 'export XDG_SESSION_DESKTOP="xfce"' >> ~/.vnc/xstartup && \
    echo '' >> ~/.vnc/xstartup && \
    echo '# Start dbus' >> ~/.vnc/xstartup && \
    echo 'if [ -z "$DBUS_SESSION_BUS_ADDRESS" ]; then' >> ~/.vnc/xstartup && \
    echo '    eval $(dbus-launch --sh-syntax --exit-with-session)' >> ~/.vnc/xstartup && \
    echo 'fi' >> ~/.vnc/xstartup && \
    echo '' >> ~/.vnc/xstartup && \
    echo '# Set background to solid color' >> ~/.vnc/xstartup && \
    echo 'xsetroot -solid grey' >> ~/.vnc/xstartup && \
    echo '' >> ~/.vnc/xstartup && \
    echo '# Start window manager' >> ~/.vnc/xstartup && \
    echo 'startxfce4 &' >> ~/.vnc/xstartup && \
    echo '' >> ~/.vnc/xstartup && \
    echo '# Keep session alive' >> ~/.vnc/xstartup && \
    echo 'wait' >> ~/.vnc/xstartup && \
    chmod +x ~/.vnc/xstartup

# Create XFCE config directory
RUN mkdir -p ~/.config/xfce4/xfconf/xfce-perchannel-xml

# Create XFCE session config using echo commands
RUN echo '<?xml version="1.0" encoding="UTF-8"?>' > ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-session.xml && \
    echo '<channel name="xfce4-session" version="1.0">' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-session.xml && \
    echo '  <property name="startup" type="empty">' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-session.xml && \
    echo '    <property name="screensaver" type="empty">' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-session.xml && \
    echo '      <property name="enabled" type="bool" value="false"/>' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-session.xml && \
    echo '    </property>' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-session.xml && \
    echo '  </property>' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-session.xml && \
    echo '  <property name="shutdown" type="empty">' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-session.xml && \
    echo '    <property name="ShowHibernate" type="bool" value="false"/>' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-session.xml && \
    echo '    <property name="ShowSuspend" type="bool" value="false"/>' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-session.xml && \
    echo '  </property>' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-session.xml && \
    echo '</channel>' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-session.xml

USER root

# Install requirements and Goose
COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt
RUN pip3 install goose-ai

# Create directories
RUN mkdir -p /home/goose/workspace && \
    chown -R goose:goose /home/goose/

# Create scripts directory and copy API
RUN mkdir -p /home/goose/scripts
COPY scripts/ /home/goose/scripts/
RUN chown -R goose:goose /home/goose/scripts
    
# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5901 6080

USER goose
ENTRYPOINT ["/entrypoint.sh"]