#!/bin/bash
x11vnc -display :${DISPLAY_NUM} -forever -shared -rfbport 5900 -bg -o /tmp/x11vnc.log
echo "Started x11vnc server on port 5900"
