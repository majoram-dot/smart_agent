"""
test_imports.py — 验证 smart_agent 所有核心子包可被正确导入
"""
import sys
import os

# 确保 src/ 在路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_package_version():
    """测试顶层包可以正常导入，且版本号存在"""
    import smart_agent
    assert hasattr(smart_agent, "__version__")
    assert smart_agent.__version__ == "0.1.0"


def test_core_tools_importable():
    """测试 core_tools 模块可以独立导入"""
    from smart_agent.core_tools import Tool, tool, BaseTool, ToolCollection
    assert Tool is not None
    assert BaseTool is not None


def test_tools_package_importable():
    """测试 tools 子包可以正常导入"""
    from smart_agent.tools import NoteTool, TerminalTool, Tool
    assert NoteTool is not None
    assert TerminalTool is not None


def test_memory_package_importable():
    """测试 memory 子包可以正常导入"""
    from smart_agent.memory import (
        MemoryItem, BaseMemory, WorkingMemory,
        EpisodicMemory, MemoryManager,
    )
    assert MemoryItem is not None
    assert MemoryManager is not None


def test_core_memory_importable():
    """测试 core_memory（Agent步骤类）可以正常导入"""
    from smart_agent.core_memory import (
        AgentMemory, ActionStep, TaskStep, PlanningStep,
        ToolCall, CallbackRegistry,
    )
    assert AgentMemory is not None


def test_rag_package_importable():
    """测试 RAG 子包可以正常导入（不需要可选依赖）"""
    try:
        from smart_agent.rag import VectorStore, MQESearch, HyDESearch, HybridSearch
        assert VectorStore is not None
    except ImportError as e:
        # RAG 可能依赖未安装的可选包，此时跳过而非失败
        import pytest
        pytest.skip(f"RAG 可选依赖未安装: {e}")


def test_memory_item_creation():
    """测试 MemoryItem 可以被实例化"""
    import uuid
    from smart_agent.memory import MemoryItem
    item = MemoryItem(id=str(uuid.uuid4()), content="测试记忆内容", memory_type="working")
    assert item.content == "测试记忆内容"
    assert item.memory_type == "working"


def test_working_memory_operations():
    """测试 WorkingMemory 的基本增删查操作"""
    from smart_agent.memory import WorkingMemory
    mem = WorkingMemory(user_id="test_user", capacity=10)
    mem.add(content="工作记忆测试", importance=0.8)
    retrieved = mem.get_all()
    assert len(retrieved) >= 1
    assert any(i.content == "工作记忆测试" for i in retrieved)


def test_hybrid_search_instantiation():
    """测试 HybridSearch 类能被实例化（不实际执行检索）"""
    try:
        from smart_agent.rag import HybridSearch
        # 不传入实际 vector_store，仅测试类的可构造性
        hs = HybridSearch(vector_store=None, embeddings=None)
        assert hs is not None
    except ImportError as e:
        import pytest
        pytest.skip(f"RAG 可选依赖未安装: {e}")
