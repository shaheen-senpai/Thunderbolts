import os
from typing import List, Dict, Any, Optional
from llama_index.core import Settings
from llama_index.core.tools import FunctionTool
from llama_index.llms.anthropic import Anthropic
from llama_index.core.callbacks import CallbackManager, LlamaDebugHandler
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.agent.workflow import FunctionAgent
import dotenv

# For web search capability
from llama_index.tools.tavily_research import TavilyToolSpec

# For observability
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
dotenv.load_dotenv()

# Set up debug handler for observability
llama_debug = LlamaDebugHandler()
callback_manager = CallbackManager([llama_debug])

# Configure LLM
llm = Anthropic(model=os.getenv("ANTHROPIC_MODEL_NAME"), temperature=float(os.getenv("DEFAULT_TEMPERATURE", 0.2)))

# Configure global settings
Settings.llm = llm
Settings.callback_manager = callback_manager


class IntelligentChatbot:
    """Intelligent chatbot system with internet search capability and specialized agents."""

    def __init__(self):
        """Initialize the chatbot system."""
        # Memory for conversation context
        memory_token_limit = int(os.getenv("MEMORY_TOKEN_LIMIT", 3000))
        self.memory = ChatMemoryBuffer.from_defaults(token_limit=memory_token_limit)

        # Create the main agent with tools
        self.agent = self._create_main_agent()

        # Specialized agents
        self.specialized_agents = self._create_specialized_agents()

        # For tracking conversation state
        self.conversation_state = {
            "needs_internet_search": False,
            "last_topic": None,
            "current_agent": "main"
        }

        logger.info("Intelligent chatbot initialized and ready")

    def _create_main_agent(self) -> FunctionAgent:
        """Create the main agent with all necessary tools."""
        # Define tools
        search_tool = TavilyToolSpec(
            api_key=os.getenv("TAVILY_API_KEY"),
        ).to_tool_list()
        # weather_tools = OpenWeatherMapToolSpec(
        #     key=os.getenv("OPENWEATHERMAP_API_KEY"),
        # ).to_tool_list()

        # Custom tools
        calculator_tool = FunctionTool.from_defaults(
            fn=self._calculator,
            name="calculator",
            description="Useful for performing mathematical calculations"
        )

        delegate_tool = FunctionTool.from_defaults(
            fn=self._delegate_to_specialized_agent,
            name="delegate_to_specialized_agent",
            description="Delegates a task to a specialized agent when the task requires specific expertise"
        )

        # Combine all tools
        tools = search_tool + [calculator_tool, delegate_tool]
        # + weather_tools

        # Create agent with memory - updated to current API
        agent = FunctionAgent(
            tools=tools,
            llm=llm,
            memory=self.memory,
            verbose=True,
            system_prompt="""
            You are an intelligent assistant that can help with a wide range of tasks.
            When you don't know something or when information might be outdated, use the search tool to find current information.
            For specialized tasks, consider delegating to a specialized agent.
            Always provide helpful, accurate, and concise responses.
            """,
        )

        return agent

    def _create_specialized_agents(self) -> Dict[str, Any]:
        """Create specialized agents for specific domains."""
        # Research agent with enhanced search capabilities
        research_agent = FunctionAgent(
            tools=[],
            llm=Anthropic(model=os.getenv("ANTHROPIC_MODEL_NAME"), temperature=float(os.getenv("RESEARCH_TEMPERATURE", 0.1))),
            system_prompt="""
            You are a research specialist. Your task is to perform in-depth research on topics,
            synthesize information from multiple sources, and provide comprehensive analysis.
            Always cite your sources and evaluate the credibility of information.
            """,
        )

        # Technical documentation agent
        tech_agent = FunctionAgent(
            tools=[],  # No specific tools needed
            llm=Anthropic(model=os.getenv("ANTHROPIC_MODEL_NAME"), temperature=float(os.getenv("TECHNICAL_TEMPERATURE", 0.1))),
            system_prompt="""
            You are a technical documentation specialist. Your task is to explain technical concepts clearly,
            provide code examples when appropriate, and follow best practices in technical writing.
            Focus on accuracy, clarity, and practical applicability.
            """,
        )

        # Creative content agent
        creative_agent = FunctionAgent(
            tools=[],  # No specific tools needed
            # Higher temperature for creativity
            llm=Anthropic(model=os.getenv("ANTHROPIC_MODEL_NAME"), temperature=float(os.getenv("CREATIVE_TEMPERATURE", 0.7))),
            system_prompt="""
            You are a creative content specialist. Your task is to generate creative content,
            including stories, marketing copy, and innovative ideas. Think outside the box
            and provide content that is engaging, original, and tailored to the specific needs.
            """,
        )

        return {
            "research": research_agent,
            "technical": tech_agent,
            "creative": creative_agent
        }

    def _calculator(self, expression: str) -> str:
        """Simple calculator tool."""
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return f"Result: {result}"
        except Exception as e:
            return f"Error in calculation: {str(e)}"

    async def _delegate_to_specialized_agent(self, task: str, agent_type: str) -> str:
        """Delegate a task to a specialized agent."""
        if agent_type not in self.specialized_agents:
            return f"Error: Agent type '{agent_type}' not found. Available agents: {list(self.specialized_agents.keys())}"
    
        agent = self.specialized_agents[agent_type]
        self.conversation_state["current_agent"] = agent_type
    
        try:
            response = await agent.run(user_msg=task, memory=self.memory)
    
            # Log the response for debugging
            logger.info(f"Specialized agent response: {str(response)}")
    
            # Extract the response text
            response_text = response.get("output", str(response))
        except Exception as e:
            logger.error(f"Error with specialized agent: {str(e)}")
            response_text = f"The {agent_type} agent encountered an error: {str(e)}"
    
        # Reset to main agent after completion
        self.conversation_state["current_agent"] = "main"
    
        return response_text

    def _detect_internet_search_need(self, query: str) -> bool:
        """Determine if a query likely requires internet search."""
        # Keywords that suggest current information is needed
        current_info_keywords = [
            "latest", "recent", "current", "today", "news",
            "update", "happening", "now", "weather", "forecast",
            "price", "stock", "market", "event", "release"
        ]

        # Check for question patterns that typically require factual/current info
        question_indicators = ["what is", "who is",
                               "when is", "where is", "how to", "why is"]

        # Simple heuristic: check for keywords and question patterns
        needs_search = any(keyword in query.lower()
                           for keyword in current_info_keywords)
        needs_search = needs_search or any(
            indicator in query.lower() for indicator in question_indicators)

        return needs_search

    def _determine_best_agent(self, query: str) -> str:
        """Determine which specialized agent would be best for a given query."""
        # Simple keyword-based routing for demonstration
        if any(word in query.lower() for word in ["research", "analyze", "investigate", "find", "search"]):
            return "research"
        elif any(word in query.lower() for word in ["code", "program", "function", "technical", "explain"]):
            return "technical"
        elif any(word in query.lower() for word in ["create", "write", "imagine", "story", "creative"]):
            return "creative"
        else:
            return "main"  # Default to main agent

    async def process_query(self, query: str) -> str:
        """Process a user query and return a response."""
        logger.info(f"Processing query: {query}")
    
        # Update conversation state
        self.conversation_state["needs_internet_search"] = self._detect_internet_search_need(query)
        print(f"Needs internet search: {self.conversation_state['needs_internet_search']}")
    
        # Determine best agent for the query
        best_agent = self._determine_best_agent(query)
        print(f"Best agent determined: {best_agent}")
    
        # If we need a specialized agent, delegate
        if best_agent != "main":
            logger.info(f"Delegating to {best_agent} agent")
            return await self._delegate_to_specialized_agent(query, best_agent)
    
        # Otherwise use the main agent
        logger.info("Using main agent")
        response = await self.agent.run(user_msg=query)
        print(f"Response type: {type(response)}")
    
        # Log the response for debugging
        logger.info(f"Response: {str(response)}")
    
        # Extract the response text, assuming it's in the 'output' field
        response_text = response.get("output", str(response))
    
        return response_text


class ChatbotAPI:
    """API wrapper for the chatbot."""

    def __init__(self):
        self.chatbot = IntelligentChatbot()

    async def handle_message(self, message: str) -> Dict[str, Any]:
        """Handle an incoming message and return a response."""
        try:
            response = await self.chatbot.process_query(message)
            return {
                "status": "success",
                "message": response,
                "used_internet_search": self.chatbot.conversation_state["needs_internet_search"],
                "agent_used": self.chatbot.conversation_state["current_agent"]
            }
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "status": "error",
                "message": "I encountered an error while processing your request.",
                "error": str(e)
            }

    def reset(self) -> Dict[str, Any]:
        """Reset the chatbot's memory and state."""
        self.chatbot = IntelligentChatbot()
        return {
            "status": "success",
            "message": "Chatbot reset successfully"
        }


# Example usage
if __name__ == "__main__":
    import asyncio

    api = ChatbotAPI()

    # Example conversation
    queries = [
        "What's the weather like in New York today?",
        "Can you help me understand how transformers work in machine learning?",
        "Write a short story about a robot who discovers emotions",
        "What's the latest news about climate change?",
        "Calculate 235 * 18.7"
    ]

    async def main():
        for query in queries:
            print(f"\nUser: {query}")
            response = await api.handle_message(query)
            print(f"Chatbot: {response['message']}")
            print(f"Used internet search: {response['used_internet_search']}")
            print(f"Agent used: {response['agent_used']}")

    asyncio.run(main())
