#!/bin/bash
Xvfb :${DISPLAY_NUM} -screen 0 ${WIDTH}x${HEIGHT}x24 &
echo "Started Xvfb on display :${DISPLAY_NUM} with resolution ${WIDTH}x${HEIGHT}"
