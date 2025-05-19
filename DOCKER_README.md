# Unstuck AI Docker Container

This Docker container runs both the Unstuck AI MCP server and Goose in a single environment, making it easy to use them together.

## Prerequisites

- Docker
- Docker Compose

## Setup

1. Make sure you have Docker and Docker Compose installed on your system.

2. Create a `.env` file in the project root based on the provided `.env.example`:
   ```bash
   cp .env.example .env
   ```
   
   Then edit the `.env` file to add your Nostr private key and other required configuration:
   ```
   # Nostr private key in hex format (this is for the agent's Nostr account)
   NOSTR_PRIVATE_KEY=your_private_key_here
   NWC_KEY=your_nwc_key_here
   
   # For file uploads to digital ocean (for screenshots)
   DIGITAL_OCEAN_SPACES_ACCESS_KEY=your_access_key
   DIGITAL_OCEAN_SPACES_SECRET_KEY=your_secret_key
   DIGITAL_OCEAN_SPACE_NAME=your_space_name
   ```

3. Build and run the container:
   ```bash
   docker-compose up --build
   ```

## Accessing the Container

Once the container is running, you can access it in two ways:

1. **VNC Web Interface**: Open your browser and go to:
   ```
   http://localhost:6080/vnc.html
   ```
   This will give you access to the virtual desktop environment where you can interact with Goose.

2. **MCP Server API**: The MCP server is accessible at:
   ```
   http://localhost:8000
   ```

## Using Goose with the MCP Server

1. Access the virtual desktop using the VNC web interface.

2. Open a terminal in the virtual desktop (right-click on the desktop and select "Terminal").

3. Run Goose with the following command:
   ```bash
   goose session --with-remote-extension http://127.0.0.1:8000/sse
   ```

4. You can now interact with Goose, and it will use the MCP server for visual tasks.

## Example Prompt

Try using this prompt with Goose:

```
can you use the unstuck ai tool to get help so I can open safari on my machine? First take a screenshot of my screen, save it and print the file path, and then give that file path when you call the tool. There are lots of screenshots, so make sure you save the screenshot with a timestamp and record that timestamp so you use the right screenshot

This is a robust way to take screenshots:

timestamp=$(date +"%Y%m%d_%H%M%S")
output_path="/home/unstuck/screenshot_$timestamp.png"
cp /tmp/screenshot.png "$output_path"
echo "Screenshot saved at: $output_path"

Make sure the file exists before calling the unstuck ai tool
```

## Stopping the Container

To stop the container, press `Ctrl+C` in the terminal where you ran `docker-compose up`, or run:

```bash
docker-compose down
```

## Troubleshooting

- If you encounter issues with the VNC connection, try refreshing the browser page.
- If Goose doesn't connect to the MCP server, make sure the MCP server is running correctly by checking the logs.
- If you need to restart the MCP server without rebuilding the entire container, you can use `docker-compose restart`.
