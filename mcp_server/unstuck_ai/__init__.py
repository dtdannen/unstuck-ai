import argparse
from .server import mcp


def main():
    """MCP Server for requesting visual computer interaction help through Nostr."""
    parser = argparse.ArgumentParser(
        description="MCP Server that connects to Nostr to request visual computer interaction help."
    )
    parser.parse_args()
    mcp.run()


if __name__ == "__main__":
    main()
