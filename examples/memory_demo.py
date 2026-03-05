import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from smart_agent.memory import (
    MemoryItem,
    WorkingMemory,
    EpisodicMemory,
    SemanticMemory,
    PerceptualMemory,
    MemoryManager,
    MemoryTool,
)


def memory_types_demo():
    print("=" * 80)
    print("Memory Types Demo")
    print("=" * 80)
    
    print("\n1. Working Memory (Short-term)")
    print("   - For temporary information storage")
    print("   - Limited capacity")
    print("   - Quick access")
    
    working_mem = WorkingMemory(max_size=10)
    item1 = MemoryItem(content="Current task: Build SmartAgent", importance=0.9)
    item2 = MemoryItem(content="Next step: Test the system", importance=0.7)
    
    working_mem.add(item1)
    working_mem.add(item2)
    print(f"   ✓ Added 2 items to working memory")
    print(f"   ✓ Working memory size: {len(working_mem)}")
    
    print("\n2. Episodic Memory (Events)")
    print("   - Stores personal experiences")
    print("   - Time-stamped events")
    print("   - Context-rich memories")
    
    episodic_mem = EpisodicMemory()
    event1 = MemoryItem(
        content="Started SmartAgent project",
        timestamp="2026-03-03T10:00:00",
        metadata={"event": "project_start"}
    )
    episodic_mem.add(event1)
    print(f"   ✓ Added episodic memory")
    
    print("\n3. Semantic Memory (Knowledge)")
    print("   - Stores facts and concepts")
    print("   - General knowledge")
    print("   - Relationships between entities")
    
    semantic_mem = SemanticMemory()
    fact1 = MemoryItem(
        content="SmartAgent: Advanced AI Agent Framework",
        metadata={"category": "project_info"}
    )
    semantic_mem.add(fact1)
    print(f"   ✓ Added semantic memory")
    
    print("\n4. Perceptual Memory (Sensory)")
    print("   - Stores sensory inputs")
    print("   - Images, audio, etc.")
    print("   - Raw perceptual data")
    
    perceptual_mem = PerceptualMemory()
    percept1 = MemoryItem(
        content="Image: Project architecture diagram",
        metadata={"type": "image", "format": "png"}
    )
    perceptual_mem.add(percept1)
    print(f"   ✓ Added perceptual memory")


def memory_manager_demo():
    print("\n" + "=" * 80)
    print("Memory Manager Demo")
    print("=" * 80)
    
    print("\n1. Initializing MemoryManager...")
    manager = MemoryManager()
    print("   ✓ MemoryManager initialized")
    
    print("\n2. Adding memories...")
    manager.add_working_memory("Remember to test the RAG system", importance=0.8)
    manager.add_episodic_memory("Had a great brainstorming session", "2026-03-03T14:00:00")
    manager.add_semantic_memory("Python 3.11+ is required", "technical")
    
    print("   ✓ Working memory added")
    print("   ✓ Episodic memory added")
    print("   ✓ Semantic memory added")
    
    print("\n3. Retrieving memories...")
    working = manager.get_working_memory()
    episodic = manager.get_episodic_memory()
    semantic = manager.get_semantic_memory()
    
    print(f"   ✓ Working memories: {len(working)}")
    print(f"   ✓ Episodic memories: {len(episodic)}")
    print(f"   ✓ Semantic memories: {len(semantic)}")
    
    print("\n4. Searching memories...")
    results = manager.search("RAG")
    print(f"   ✓ Search results: {len(results)}")


def memory_tool_demo():
    print("\n" + "=" * 80)
    print("Memory Tool Demo")
    print("=" * 80)
    
    print("\n1. MemoryTool integrates all memory types")
    print("   - Unified interface for memory operations")
    print("   - Easy to use with agents")
    print("   - Supports CRUD operations")


def main():
    memory_types_demo()
    memory_manager_demo()
    memory_tool_demo()
    
    print("\n" + "=" * 80)
    print("Memory Demo completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
