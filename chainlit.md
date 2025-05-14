theme:
primary_color: "#19C37D"
font_family: "Söhne, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, sans-serif"
background_color: "#343541"
message:
user_background_color: "#343541"
assistant_background_color: "#444654"
user_bubble_color: "#343541"
assistant_bubble_color: "#444654"
user_text_color: "#FFFFFF"
assistant_text_color: "#FFFFFF"
chat_input:
background_color: "#40414F"
border_color: "#565869"
placeholder_color: "#8E8EA0"
text_color: "#FFFFFF"

chainlit:

# The name of the app and page title

name: "ChatGPT Clone"

# The description of the app

description: "Powered by Anthropic's Claude & LlamaIndex"

# The favicon of the app

favicon: "https://chat.openai.com/favicon.ico"

# UI customization options

ui: # Whether to show the app information as a side panel (false to mimic ChatGPT)
show_app_info: false # Customize the default collapsed state of the settings panel
default_collapse_settings: true # Customize the default collapsed state of the message settings
default_collapse_message_settings: true # Hide the watermark to mimic ChatGPT
hide_watermark: true

# Header settings

header:

# Whether to show the header

visible: true

# The title in the header

title: "ChatGPT"

# The logo in the header

logo: "https://chat.openai.com/apple-touch-icon.png"

# Allow users to upload files

features:

# Whether to enable file uploads

file_upload: true

# Whether to enable the copy button for chat messages

copy_messages: true

# Whether to enable chat history

chat_history: true

# Whether to enable search

search: false

# Whether to use a more minimal UI (like ChatGPT)

minimal_ui: true

# Message settings

messages:

# The name to display for the assistant (ChatGPT)

assistant_name: "ChatGPT"

# Add spacing between messages like in ChatGPT

message_spacing: "12px"

# Code highlighting settings

code:

# The theme for code highlighting

theme: "github-dark"

# Optionally configure avatars

avatars:

# URL for the assistant avatar - using ChatGPT icon

assistant: "https://chat.openai.com/apple-touch-icon.png"

# URL for the user avatar - using a simple user icon

user: "https://www.gravatar.com/avatar/default?s=200&d=identicon"
