from langchain.agents import AgentExecutor, Tool, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import DuckDuckGoSearchResults
import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BlogGenerator:
    def __init__(self):
        try:
            self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
            
            # Initialize tools
            wikipedia = WikipediaAPIWrapper()
            duckduckgo = DuckDuckGoSearchResults()
            
            self.tools = [
                Tool(
                    name="Wikipedia",
                    func=wikipedia.run,
                    description="Useful for accessing factual information from Wikipedia articles."
                ),
                Tool(
                    name="DuckDuckGo_Search",
                    func=duckduckgo.run,
                    description="Useful for finding recent and diverse information from the web."
                )
            ]
            
            self.prompt = ChatPromptTemplate.from_messages([
                        ("system", """You are a professional blog writer. Your task is to generate a well-structured blog post on a given topic. 

            Follow these steps:
            1. Use the tools provided to research the topic thoroughly.
            2. Compose a blog with the following sections:
            - Heading: Clear and engaging title.
            - Introduction: Overview and hook to engage readers.
            - Content: Detailed, well-researched information with sources cited.
            - Summary: Concise recap of key points.

            Ensure the blog is accurate, coherent, and properly formatted."""),
                        MessagesPlaceholder(variable_name="chat_history", optional=True),
                        ("human", "{input}"),
                        MessagesPlaceholder(variable_name="agent_scratchpad")
                    ])
            
            # Create the agent
            self.agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
            self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
        except Exception as e:
            logger.error(f"Error initializing BlogGenerator: {e}")
            raise

    def generate_blog(self, topic: str) -> str:
        """Generates a structured blog post on the given topic."""
        try:
            response = self.agent_executor.invoke({"input": f"Write a blog about: {topic}"})
            return response["output"]
        except Exception as e:
            logger.error(f"Error generating blog for topic '{topic}': {e}")
            return "An error occurred while generating the blog."

if __name__ == "__main__":
    generator = BlogGenerator()
    blog = generator.generate_blog("Enter_your_topic_here")
    print("\nGenerated Blog:\n")
    print(blog)

