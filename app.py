import os
import chainlit as cl
from typing import Dict, Any
from chainlit.element import Element
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

# Import our intelligent chatbot implementation
from intelligent_chatbot import ChatbotAPI, IntelligentChatbot

# Initialize the chatbot API
api = ChatbotAPI()


@cl.on_chat_start
async def on_chat_start():
    """Initialize the chat session when a user connects."""
    # Set page title and description - minimal welcome message like ChatGPT
    await cl.Message(
        content="How can I help you today?",
        author="ChatGPT"
    ).send()

    # Create and store a reference to our chatbot instance
    chatbot = api.chatbot
    cl.user_session.set("chatbot", chatbot)

    # Add reset button but make it less prominent, more like the "New chat" in ChatGPT
    actions = [
        cl.Action(name="reset", label="New Chat", payload={},
                  description="Start a new conversation")
    ]
    
    # We'll place the reset button in a very minimal footer message
    # This is hidden until the first message is sent
    cl.user_session.set("has_sent_message", False)


@cl.action_callback("reset")
async def on_reset(action):
    """Handle the reset button click - create a new chat."""
    # Reset the chatbot
    reset_response = api.reset()
    new_chatbot = api.chatbot
    cl.user_session.set("chatbot", new_chatbot)
    cl.user_session.set("has_sent_message", False)
    
    # Clear the chat interface
    await cl.Message(content="Starting a new chat...", author="System").send()
    
    # Redirect to a new chat session (this will create a new chat in the UI)
    await cl.Message(content="How can I help you today?", author="ChatGPT").send()
    
    # Remove the action after it's been clicked
    await action.remove()


@cl.on_message
async def on_message(message: cl.Message):
    """Process incoming messages."""
    user_message = message.content

    chatbot = cl.user_session.get("chatbot")
    if not chatbot:
        chatbot = api.chatbot
        cl.user_session.set("chatbot", chatbot)
    
    # Set message sent flag
    has_sent_message = cl.user_session.get("has_sent_message", False)
    if not has_sent_message:
        cl.user_session.set("has_sent_message", True)
        # Add the new chat button after first message
        actions = [
            cl.Action(name="reset", label="New Chat", payload={},
                    description="Start a new conversation")
        ]
        await cl.Message(content="", actions=actions).send()

    # Use a step with no name to mimic ChatGPT's minimal UI
    async with cl.Step() as step:
        # Show typing indicator like ChatGPT
        await cl.Message(content="", author="ChatGPT", is_loading=True).send()
        
        response_dict = await api.handle_message(user_message)

        if response_dict["status"] == "error":
            await cl.Message(
                content=f"I encountered an error: {response_dict['error']}",
                author="ChatGPT"
            ).send()
            return

        response_content = response_dict["message"]
        
        # In ChatGPT style, we don't show the agent info in the UI
        # Instead, just display the response cleanly
        await cl.Message(content=response_content, author="ChatGPT").update()
        
        # Store this information in session for debugging if needed
        cl.user_session.set("used_internet_search", response_dict["used_internet_search"])
        cl.user_session.set("agent_used", response_dict["agent_used"])


@cl.on_settings_update
async def on_settings_update(settings):
    """Handle settings updates."""
    # In ChatGPT style, settings changes are less visible
    # We'll just acknowledge them quietly
    cl.user_session.set("settings_updated", settings)

if __name__ == "__main__":
    # Run the app with the command: chainlit run app.py
    pass
