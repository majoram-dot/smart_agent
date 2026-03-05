import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from smart_agent import CodeAgent, PythonInterpreterTool, FinalAnswerTool
from smart_agent.tools import NoteTool, TerminalTool
from dotenv import load_dotenv

load_dotenv()


def basic_agent_demo():
    print("=" * 80)
    print("Basic Agent Demo")
    print("=" * 80)
    
    tools = [
        PythonInterpreterTool(),
        FinalAnswerTool(),
    ]
    
    try:
        agent = CodeAgent(tools=tools)
        
        print("\nRunning agent task: 'Calculate 2 + 2'")
        result = agent.run("Calculate 2 + 2")
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: You need to configure an LLM model to run the full agent.")


def note_tool_demo():
    print("\n" + "=" * 80)
    print("Note Tool Demo")
    print("=" * 80)
    
    notes = NoteTool(workspace="./demo_notes")
    
    print("\n1. Creating a note...")
    create_result = notes.run({
        "action": "create",
        "title": "SmartAgent Project",
        "content": """# SmartAgent Project

This is a demo note for the SmartAgent framework.

## Features:
- Multi-step agents
- RAG system
- Memory system
- Various tools
""",
        "note_type": "project",
        "tags": ["smartagent", "demo", "ai"]
    })
    print(create_result)
    
    print("\n2. Listing notes...")
    list_result = notes.run({"action": "list", "limit": 5})
    print(list_result)
    
    print("\n3. Getting summary...")
    summary_result = notes.run({"action": "summary"})
    print(summary_result)


def terminal_tool_demo():
    print("\n" + "=" * 80)
    print("Terminal Tool Demo")
    print("=" * 80)
    
    terminal = TerminalTool(workspace="./")
    
    print("\n1. Listing current directory...")
    result = terminal.run({"command": "dir" if os.name == "nt" else "ls -la"})
    print(result)


if __name__ == "__main__":
    basic_agent_demo()
    note_tool_demo()
    terminal_tool_demo()
    
    print("\n" + "=" * 80)
    print("Demo completed!")
    print("=" * 80)
