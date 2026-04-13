from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
import os

load_dotenv()

def agent(tools):
    llm = ChatGroq(api_key=os.getenv("GEMINI_API"), model="llama-3.3-70b-versatile").bind_tools(tools)
    executor = create_react_agent(llm, tools)
    return executor