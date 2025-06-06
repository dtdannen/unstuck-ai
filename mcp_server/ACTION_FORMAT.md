# MCP Server Action Format Documentation

## Overview

The Unstuck MCP server expects actions to be sent in a specific JSON format within kind 6109 Nostr events. Actions use percentage-based coordinates (0-100) that are automatically converted to actual screen coordinates.

## Coordinate System

- **X coordinate**: 0-100 (percentage of screen width)
- **Y coordinate**: 0-100 (percentage of screen height)
- Example: `{"x": 50, "y": 50}` represents the center of the screen

## Action Types

### 1. Click
Single mouse click at specified coordinates.

```json
{
  "type": "click",
  "x": 50,
  "y": 30
}
```

### 2. Double Click
Double mouse click at specified coordinates.

```json
{
  "type": "doubleClick",
  "x": 75,
  "y": 25
}
```

### 3. Drag
Drag from start to end coordinates.

```json
{
  "type": "drag",
  "start": {"x": 20, "y": 40},
  "end": {"x": 80, "y": 60}
}
```

### 4. Move Mouse
Move mouse to coordinates without clicking.

```json
{
  "type": "moveMouse",
  "x": 10,
  "y": 90
}
```

Alternative type name: `"move"` also works.

## Complete Example

A kind 6109 Nostr event should contain actions in the following format:

```json
{
  "actions": [
    {
      "type": "moveMouse",
      "x": 50,
      "y": 50
    },
    {
      "type": "click",
      "x": 50,
      "y": 50
    },
    {
      "type": "drag",
      "start": {"x": 30, "y": 30},
      "end": {"x": 70, "y": 70}
    }
  ]
}
```

## Response Format

The server will execute actions and return results:

```json
{
  "success": true,
  "actions_executed": 3,
  "results": [
    {"index": 0, "type": "moveMouse", "success": true},
    {"index": 1, "type": "click", "success": true},
    {"index": 2, "type": "drag", "success": true}
  ]
}
```

## Notes

1. Actions are executed sequentially with a 0.2 second delay between each action
2. All coordinates must be percentages (0-100), not absolute pixel values
3. The server automatically converts percentages to actual screen coordinates
4. PyAutoGUI must be available on the server for actions to execute