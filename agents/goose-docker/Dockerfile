# /agents/goose-docker/Dockerfile

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

## Install system dependencies with proper X11, desktop components, and automation tools
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
    libgtk-3-0 \
    libasound2 \
    libdbus-glib-1-2 \
    # Screenshot and automation tools
    scrot \
    imagemagick \
    gnome-screenshot \
    python3-xlib \
    python3-tk \
    python3-dev \
    # Additional tools for PyAutoGUI
    python3-pil \
    python3-pil.imagetk \
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

# Create Goose config directory
RUN mkdir -p ~/.config/goose

# Copy the custom goose configuration files
COPY agents/goose-docker/config/goose_config.yaml /home/goose/.config/goose/profiles.yaml
COPY agents/goose-docker/config/config.yaml /home/goose/.config/goose/config.yaml

# Copy MCP server configuration to where Block's Goose expects it
COPY agents/goose-docker/config/mcp_servers.json /home/goose/.config/goose/mcp_servers.json

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

# Create Desktop directory and browser shortcuts
RUN mkdir -p ~/Desktop && \
    echo '[Desktop Entry]' > ~/Desktop/firefox.desktop && \
    echo 'Version=1.0' >> ~/Desktop/firefox.desktop && \
    echo 'Type=Application' >> ~/Desktop/firefox.desktop && \
    echo 'Name=Firefox' >> ~/Desktop/firefox.desktop && \
    echo 'Comment=Browse the Web' >> ~/Desktop/firefox.desktop && \
    echo 'Exec=/usr/bin/firefox %u' >> ~/Desktop/firefox.desktop && \
    echo 'Terminal=false' >> ~/Desktop/firefox.desktop && \
    echo 'Icon=firefox' >> ~/Desktop/firefox.desktop && \
    echo 'Categories=Network;WebBrowser;' >> ~/Desktop/firefox.desktop && \
    echo 'MimeType=text/html;text/xml;application/xhtml+xml;application/xml;application/vnd.mozilla.xul+xml;application/rss+xml;application/rdf+xml;image/gif;image/jpeg;image/png;x-scheme-handler/http;x-scheme-handler/https;' >> ~/Desktop/firefox.desktop && \
    echo 'StartupNotify=true' >> ~/Desktop/firefox.desktop && \
    chmod +x ~/Desktop/firefox.desktop

# Create XFCE session config to disable screensaver and power management
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

# Disable power manager to prevent plugin errors
RUN echo '<?xml version="1.0" encoding="UTF-8"?>' > ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml && \
    echo '<channel name="xfce4-power-manager" version="1.0">' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml && \
    echo '  <property name="xfce4-power-manager" type="empty">' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml && \
    echo '    <property name="power-button-action" type="uint" value="0"/>' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml && \
    echo '    <property name="show-tray-icon" type="bool" value="false"/>' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml && \
    echo '  </property>' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml && \
    echo '</channel>' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml

# Disable screensaver completely
RUN echo '<?xml version="1.0" encoding="UTF-8"?>' > ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '<channel name="xfce4-screensaver" version="1.0">' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '  <property name="saver" type="empty">' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '    <property name="enabled" type="bool" value="false"/>' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '    <property name="mode" type="int" value="0"/>' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '  </property>' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '  <property name="lock" type="empty">' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '    <property name="enabled" type="bool" value="false"/>' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '  </property>' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml && \
    echo '</channel>' >> ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-screensaver.xml

# Create autostart directory and disable unwanted services
RUN mkdir -p ~/.config/autostart && \
    echo '[Desktop Entry]' > ~/.config/autostart/xfce4-power-manager.desktop && \
    echo 'Hidden=true' >> ~/.config/autostart/xfce4-power-manager.desktop && \
    echo '[Desktop Entry]' > ~/.config/autostart/xscreensaver.desktop && \
    echo 'Hidden=true' >> ~/.config/autostart/xscreensaver.desktop && \
    echo '[Desktop Entry]' > ~/.config/autostart/light-locker.desktop && \
    echo 'Hidden=true' >> ~/.config/autostart/light-locker.desktop

USER root

# Install requirements
COPY agents/goose-docker/requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

# Install curl if not already installed
RUN apt-get update && apt-get install -y curl

# Install Block's Goose (the correct one with MCP support)
# Install as root first
RUN curl -fsSL https://github.com/block/goose/releases/download/stable/download_cli.sh | bash && \
    # Move goose binary to system-wide location
    mv /root/.local/bin/goose /usr/local/bin/goose && \
    chmod +x /usr/local/bin/goose

# Copy and install unstuck MCP server
# Note: mcp_server directory should be copied to the build context
COPY mcp_server /home/goose/mcp_server
RUN cd /home/goose/mcp_server && \
    pip3 install -r requirements.txt && \
    pip3 install -e . && \
    chown -R goose:goose /home/goose/mcp_server

# Create directories
RUN mkdir -p /home/goose/workspace && \
    chown -R goose:goose /home/goose/

# Create scripts directory and copy API
RUN mkdir -p /home/goose/scripts
COPY agents/goose-docker/scripts/ /home/goose/scripts/
COPY agents/goose-docker/unstuck_toolkit.py /home/goose/.config/goose/toolkits/unstuck.py
RUN chown -R goose:goose /home/goose/scripts && \
    mkdir -p /home/goose/.config/goose/toolkits && \
    chown -R goose:goose /home/goose/.config/goose/toolkits
    
# Copy entrypoint
COPY agents/goose-docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5901 6080

USER goose
ENTRYPOINT ["/entrypoint.sh"]