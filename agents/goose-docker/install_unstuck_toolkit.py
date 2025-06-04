#!/usr/bin/env python3
"""
Script to install the unstuck toolkit into Goose's toolkit registry
"""

import sys
import os
sys.path.insert(0, '/home/goose/.config/goose/toolkits')

# Import and register the unstuck toolkit
from unstuck import UnstuckToolkit

# Patch it into goose's toolkit registry
import goose.toolkit
goose.toolkit.AVAILABLE_TOOLKITS['unstuck'] = UnstuckToolkit

print("✅ Unstuck toolkit registered successfully!")