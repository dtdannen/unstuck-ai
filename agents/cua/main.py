# /agents/cua/main.py

import asyncio
import logging
import os
import sys
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Import C/ua components
try:
    from computer import Computer
    from agent import ComputerAgent, LLM, AgentLoop, LLMProvider
    from agent.ui.gradio.app import create_gradio_ui
except ImportError as e:
    print(f"❌ Error importing C/ua components: {e}")
    print("💡 Make sure you've installed: pip install cua-computer cua-agent[all]")
    sys.exit(1)


def check_environment():
    """Check if environment is properly configured"""
    required_env_vars = ["OPENAI_API_KEY"]  # or ANTHROPIC_API_KEY
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("💡 Please check your .env file")
        return False

    print("✅ Environment variables configured")
    return True


async def setup_cua_agent():
    """Initialize the C/ua agent"""
    try:
        print("🚀 Initializing C/ua environment...")

        # Setup logging
        logging.basicConfig(
            level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        # Initialize computer environment
        computer = Computer(verbosity=logging.INFO)
        print("💻 Computer environment ready")

        # Setup agent
        agent_loop = (
            AgentLoop.OPENAI
            if os.getenv("CUA_MODEL_PROVIDER") == "OPENAI"
            else AgentLoop.ANTHROPIC
        )
        model_provider = (
            LLMProvider.OPENAI
            if os.getenv("CUA_MODEL_PROVIDER") == "OPENAI"
            else LLMProvider.ANTHROPIC
        )

        agent = ComputerAgent(
            computer=computer, loop=agent_loop, model=LLM(provider=model_provider)
        )

        print("🤖 C/ua agent initialized successfully!")
        return agent

    except Exception as e:
        print(f"❌ Error setting up agent: {e}")
        raise


def start_gradio_interface():
    """Start the Gradio web interface"""
    print("\n🎨 Starting Gradio interface...")

    try:
        # Create and configure Gradio UI
        app = create_gradio_ui()

        print("\n" + "=" * 50)
        print("🌐 C/ua Agent Interface Starting!")
        print("=" * 50)
        print("📱 Interface URL: http://localhost:7860")
        print("\n💬 Example tasks to try:")
        print("   • 'Take a screenshot of my desktop'")
        print("   • 'Open Chrome and browse to google.com'")
        print("   • 'Check if my website loads correctly'")
        print("   • 'Open VS Code and create a new file'")
        print("   • 'Help me organize files on my desktop'")
        print("\n🔍 You can watch the agent work in real-time!")
        print("=" * 50 + "\n")

        # Launch interface
        app.launch(
            share=False,
            server_name="0.0.0.0",
            server_port=7860,
            show_error=True,
            quiet=False,
            inbrowser=True,  # Automatically open browser
        )

    except Exception as e:
        print(f"❌ Error starting Gradio interface: {e}")
        raise


def main():
    """Main application entry point"""
    print("🔧 C/ua Agent Startup")
    print("=" * 30)

    # Check environment
    if not check_environment():
        sys.exit(1)

    # Start interface
    start_gradio_interface()


if __name__ == "__main__":
    main()
