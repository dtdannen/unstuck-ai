# /agents/goose-docker/scripts/start_goose.py

import os
import asyncio
import gradio as gr
from goose.client import GooseClient
from goose.mcp import MCPManager
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GooseWebInterface:
    def __init__(self):
        self.goose = None
        self.mcp_manager = None
        self.setup_goose()

    def setup_goose(self):
        """Initialize Goose with MCP capabilities"""
        try:
            # Initialize MCP manager
            self.mcp_manager = MCPManager()
            self.mcp_manager.load_servers_from_config(
                "/home/goose/.config/mcp_servers.json"
            )

            # Initialize Goose client
            self.goose = GooseClient(
                model_provider=os.getenv("GOOSE_MODEL_PROVIDER", "openai"),
                model_name=os.getenv("GOOSE_MODEL_NAME", "gpt-4o"),
                mcp_manager=self.mcp_manager,
            )

            logger.info("✅ Goose initialized with MCP capabilities")

        except Exception as e:
            logger.error(f"❌ Error initializing Goose: {e}")
            raise

    async def chat_with_goose(self, message, history):
        """Chat interface for Goose"""
        try:
            # Send message to Goose
            response = await self.goose.send_message(message)

            # Add to history
            history.append([message, response])

            return history, ""

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            history.append([message, error_msg])
            return history, ""

    def take_screenshot(self):
        """Take screenshot of the desktop"""
        try:
            # Use Goose's computer control capabilities
            result = self.goose.execute_tool("screenshot", {})
            return f"Screenshot taken: {result}"
        except Exception as e:
            return f"Error taking screenshot: {e}"

    def create_interface(self):
        """Create Gradio interface"""

        with gr.Blocks(title="Goose MCP Agent") as interface:
            gr.Markdown("# 🦆 Goose MCP Agent")
            gr.Markdown("Chat with Goose agent running in Docker with MCP capabilities")

            with gr.Row():
                with gr.Column(scale=3):
                    # Chat interface
                    chatbot = gr.Chatbot(
                        label="Chat with Goose", height=400, show_label=True
                    )

                    with gr.Row():
                        msg_input = gr.Textbox(
                            placeholder="Ask Goose to help you...",
                            scale=4,
                            submit_btn=True,
                        )
                        send_btn = gr.Button("Send", scale=1)

                with gr.Column(scale=1):
                    # Control panel
                    gr.Markdown("### 🎮 Controls")

                    screenshot_btn = gr.Button("📸 Take Screenshot")
                    screenshot_output = gr.Textbox(label="Screenshot Result")

                    gr.Markdown("### 📊 Status")
                    status = gr.Textbox(
                        value="🟢 Goose Agent Running",
                        label="Status",
                        interactive=False,
                    )

            # Example prompts
            gr.Markdown("### 💡 Example Commands")
            example_buttons = [
                gr.Button("🌐 Browse to google.com"),
                gr.Button("📝 Create a new text file"),
                gr.Button("🔍 Search for Python tutorials"),
                gr.Button("📊 Take a screenshot and describe it"),
            ]

            # Event handlers
            def send_message(message, history):
                return asyncio.run(self.chat_with_goose(message, history))

            send_btn.click(
                send_message, inputs=[msg_input, chatbot], outputs=[chatbot, msg_input]
            )

            msg_input.submit(
                send_message, inputs=[msg_input, chatbot], outputs=[chatbot, msg_input]
            )

            screenshot_btn.click(self.take_screenshot, outputs=screenshot_output)

            # Example button handlers
            example_buttons[0].click(
                lambda: "Please open a web browser and navigate to google.com",
                outputs=msg_input,
            )

            example_buttons[1].click(
                lambda: "Create a new text file called 'notes.txt' on the desktop",
                outputs=msg_input,
            )

            example_buttons[2].click(
                lambda: "Search the web for Python programming tutorials and summarize the results",
                outputs=msg_input,
            )

            example_buttons[3].click(
                lambda: "Take a screenshot and describe what you see on the screen",
                outputs=msg_input,
            )

        return interface


def main():
    """Main function to start the web interface"""
    try:
        # Create Goose interface
        goose_interface = GooseWebInterface()

        # Create Gradio app
        app = goose_interface.create_interface()

        # Launch the interface
        app.launch(
            server_name="0.0.0.0", server_port=8080, share=False, show_error=True
        )

    except Exception as e:
        logger.error(f"❌ Failed to start Goose interface: {e}")
        raise


if __name__ == "__main__":
    main()
