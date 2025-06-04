# unstuck-ai

<div align="center">
  <img src="frontend/public/unstuckgoose.png" alt="Unstuck AI" width="200">
</div>

MCP server enabling AI agents to instantly pay humans sats (Bitcoin) to solve visual roadblocks (captchas, web navigation, computer use) via a Nostr marketplace. Includes the MCP server and web app for humans to bid on tasks, complete them, and get paid.

## 🎥 Video Demonstrations

- **[Project Presentation & Q&A](https://unstuck-goose.nyc3.cdn.digitaloceanspaces.com/demos/final_presentation_and_QnA.mp4)** - Complete overview of Unstuck AI, architecture, and live Q&A session
- **[Goose Agent in Docker Sandbox](https://unstuck-goose.nyc3.cdn.digitaloceanspaces.com/demos/demo_video_sandboxxed_goose_paying_invoice.mov)** - Live demo of Goose running in sandbox, paying Bitcoin invoice for human help
- **[Original Proof of Concept](https://unstuck-goose.nyc3.cdn.digitaloceanspaces.com/Screen%20Recording%202025-05-17%20at%204.52.34%E2%80%AFPM.MOV)** - First working version showing the core concept

## Quick Start with Goose

Want to use this with [Goose](https://github.com/block/goose)? See **[GOOSE_SETUP.md](GOOSE_SETUP.md)** for complete setup instructions.

> **⚠️ IMPORTANT: Goose Version Distinction**
> 
> There are two different AI assistants named "Goose":
> - **Block's Goose** (https://github.com/block/goose) - Version 1.0.x+, has MCP support with `--with-remote-extension`
> - **goose-ai** (PyPI package) - Version 0.9.x, different project, NO MCP support
> 
> This project requires **Block's Goose** for MCP integration. Install it from:
> https://block.github.io/goose/docs/getting-started/installation

1. Install dependencies: `cd mcp_server && pip install -r requirements.txt`
2. Configure environment variables in `mcp_server/.env`
3. Add the extension to your Goose config (`~/.config/goose/config.yaml`)
4. Run `goose session` and ask for visual help!

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
    - [x] provide a docker container to run an MCP based agent (like the claude computer use demo here https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo)
      - you should be able to navigate to a webpage on your computer that lets you interact with Goose running in the VM
      - it should work as if you were running it locally
      - we expect it will be easier to get automation tools working in this VM, because you can safely get goose to work with full permissions
    - [ ] get goose to execute the action that the human gives (from the result of the mcp tool call)
        - [ ] translate coordinates to correct coordinates on screen
        - [ ] get an automation library to work that performs clicking, double clicking, and dragging
    - [ ] change hosting of screenshots from digital ocean spaces to a blossom server
    - [ ] have the mcp server post a kind 1 note linking to the job to advertise it among social media and increase the odds of a human being notified more quickly

2. Unstuck Frontend (Job Board and Workspace)
    - [x] User login via Nostr
    - [x] Pull job offers from Nostr relays
    - [ ] Allow user to set a default job amount in sats
    - [x] Display job offers
    - [x] Allow user to select a job
        - [x] generate a lightning invoice for the amount
        - [x] broadcast a kind 7000 event with the invoice and price
        - [x] show a notification when the invoice was paid
            - one suggestion is to use bitconnect instead of webln + browser extension (current demo shows alby extension)
    - [x] Show a workspace like page for the user to do the work
    - [x] Send the final job result event when the user is done

3. Misc
  - [ ] Write a wiki page on kind 5109 so it shows up nicely in https://stats.dvmdash.live/kind-stats
    - example article: https://njump.me/naddr1qvzqqqrcvgpzpkscaxrqqs8nhaynsahuz6c6jy4wtfhkl2x4zkwrmc4cyvaqmxz3qqykk6twvsar2vesxq02d424
      - only needs these sections:
        - Introduction that describes the inputs (text + screenshot) and outputs (mouse movement commands)
        - example input event
        - example output event
    - instructions to write these wiki pages can be found here https://habla.news/u/dustind@dtdannen.github.io/1743798227950
    - use a 'd' tag with the value 'kind:5109' so it shows on dvmdash
    - use a 'title' tag like 'Nostr DVM Kind 5109/6109 - Visual Computer Task Help'


 
 ## How to use

Currently, the demo requires digital ocean spaces credentials for hosting the uploaded screenshots (any boto3 provider might work easily, like AWS) and it requires a Nostr Wallet Connect string (this is how the MCP Server pays the human's invoice). These should go into the .env file.

```bash
cp .env.example .env
```

Then put the credentials needed. The NOSTR_PRIVATE_KEY is for the AI agent, you probably want to generate a new one to use (i.e. it's not meant to be your personal nsec).

Set up python env

```bash
cd mcp_server/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

then start the mcp server from within the `mcp_server` folder

 ```bash
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

screencapture -x /Users/dustin/screenshot_$(date +"%Y%m%d_%H%M%S").png

This is a robust way to check for the most recent screenshot

ls -la /Users/dustin/screenshot_*.png | tail -1

Make sure the file exists before calling the unstuck ai tool
```
