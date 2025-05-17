from mcp.server.fastmcp import FastMCP

# Create a FastMCP server named "HelloWorld"
mcp = FastMCP("HelloWorld")

@mcp.tool()
def hello(name: str = "World", punctuation: str = "!") -> str:
    """
    Say hello to a name with custom punctuation.
    Args:
        name: The name to greet (default: "World")
        punctuation: The punctuation to end the greeting (default: "!")
    Returns:
        A greeting message
    """
    return f"Hello, {name}{punctuation}"

if __name__ == "__main__":
    mcp.run()
