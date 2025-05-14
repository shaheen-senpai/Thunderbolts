import os
import chainlit as cl
from typing import Dict, Any
from chainlit.element import Element

# Import our intelligent chatbot implementation
from intelligent_chatbot import ChatbotAPI, IntelligentChatbot

# Initialize the chatbot API
api = ChatbotAPI()


@cl.on_chat_start
async def on_chat_start():
    """Initialize the chat session when a user connects."""
    # Set page title and description
    await cl.Message(
        content="👋 Welcome to the Claude-powered Intelligent Assistant!",
        author="System"
    ).send()

    # Create and store a reference to our chatbot instance
    chatbot = api.chatbot
    cl.user_session.set("chatbot", chatbot)

    # Display agent information (Accordion removed; use markdown instead)
    await cl.Message(
        content="""I can help with a wide range of tasks, including:

**Available Specialized Agents**
- **Main Assistant**: General-purpose questions and tasks  
- **Research Agent**: In-depth research and information synthesis  
- **Technical Agent**: Technical explanations and documentation  
- **Creative Agent**: Creative writing and content generation  
""",
        author="System"
    ).send()

    # Add reset button
    actions = [
        cl.Action(name="reset", label="Reset Conversation", payload={},
                  description="Clear memory and start fresh")
    ]
    await cl.Message(content="Use the button below to reset our conversation at any time.", actions=actions).send()


@cl.action_callback("reset")
async def on_reset(action):
    """Handle the reset button click."""
    await cl.Message(content="Resetting conversation...").send()

    # Reset the chatbot
    reset_response = api.reset()
    new_chatbot = api.chatbot
    cl.user_session.set("chatbot", new_chatbot)

    await cl.Message(content="Conversation has been reset. How can I help you?").send()
    await action.remove()


@cl.on_message
async def on_message(message: cl.Message):
    """Process incoming messages."""
    user_message = message.content

    chatbot = cl.user_session.get("chatbot")
    if not chatbot:
        chatbot = api.chatbot
        cl.user_session.set("chatbot", chatbot)

    async with cl.Step(name="Thinking...") as step:
        response_dict = await api.handle_message(user_message)

        if response_dict["status"] == "error":
            await cl.Message(
                content=f"I encountered an error: {response_dict['error']}",
                author="Error"
            ).send()
            return

        response_content = response_dict["message"]
        used_internet = response_dict["used_internet_search"]
        agent_used = response_dict["agent_used"]

        elements = []

        if used_internet:
            elements.append(
                cl.Text(name="Internet Search",
                        content="✓ Used internet search to find information")
            )

        agent_display_names = {
            "main": "Main Assistant",
            "research": "Research Specialist",
            "technical": "Technical Documentation Specialist",
            "creative": "Creative Content Specialist"
        }

        agent_display_name = agent_display_names.get(agent_used, agent_used)
        elements.append(
            cl.Text(name="Agent Used",
                    content=f"🤖 Response from: {agent_display_name}")
        )

        await cl.Message(
            content=response_content,
            elements=elements
        ).send()


@cl.on_settings_update
async def on_settings_update(settings):
    """Handle settings updates."""
    await cl.Message(content=f"Settings updated: {settings}").send()

if __name__ == "__main__":
    pass