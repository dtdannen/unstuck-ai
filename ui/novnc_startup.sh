#!/bin/bash
/opt/noVNC/utils/novnc_proxy --vnc localhost:5900 --listen 6080 &
echo "Started noVNC proxy on port 6080"
