# unstuck-ai

<div align="center">
  <a href="https://unstuck-goose.nyc3.cdn.digitaloceanspaces.com/Screen%20Recording%202025-05-17%20at%204.52.34%E2%80%AFPM.MOV">
    <img src="frontend/public/unstuckgoose.png" alt="Unstuck AI Demo Video" width="600">
  </a>
  <p>👆 Click the image to watch the demo video 👆</p>
</div>

MCP server enabling AI agents to instantly pay humans sats (Bitcoin) to solve visual roadblocks (captchas, web navigation, computer use) via a Nostr marketplace. Includes the MCP server and web app for humans to bid on tasks, complete them, and get paid.

## Development Plan

Components:

1. MCP Server

    - [x] sends a kind 5109 event request for visual computer interaction help
    - [x] listens for feedback responses for prices and corresponding invoices
    - [x] selects an offer by paying the invoice
    - [x] receives the result, returns it as the result of the MCP tool call
    - [x] (testing) check invoice was paid in payment simulator before sending 6109
    - [x] get image upload working on digital ocean
    - [x] get goose or claude to take a screenshot and call the mcp tool correctly
    - [ ] get goose to execute the action that the human gives (from the result of the mcp tool call)

2. Unstuck Frontend (Job Board and Workspace)
    - [x] User login via Nostr
    - [x] Pull job offers from Nostr relays
    - [ ] Allow user to set a default job amount in sats
    - [x] Display job offers
    - [x] Allow user to select a job
        - [x] generate a lightning invoice for the amount
        - [x] broadcast a kind 7000 event with the invoice and price
        - [ ] show a notification when the invoice was paid
    - [x] Show a workspace like page for the user to do the work
    - [x] Send the final job result event when the user is done

 
 ## How to use

 ```bash
 cd mcp_server/
 fastmcp run unstuck_ai/server.py:mcp --transport sse
 ```

 then in another terminal run goose

 ```bash
 goose session --with-remote-extension http://127.0.0.1:8000/sse
 ```

and then you can try using it with a propmt to goose like:

```bash
( O)> can you use the unstuck ai tool to get help so I can open safari on my machine? First take a screenshot of my screen, save it and print the file path, and then give that file path when you call the tool. There are lots of screenshots, so make sure you save the screenshot with a timestamp and record that timestamp so you use the right screenshot

This is a robust way to take screenshots:

timestamp=$(date +"%Y%m%d_%H%M%S")
output_path="/Users/dustin/screenshot_$timestamp.png"
cp /tmp/screenshot.png "$output_path"
echo "Screenshot saved at: $output_path"

Make sure the file exists before calling the unstuck ai tool
```
