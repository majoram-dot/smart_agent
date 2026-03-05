"""
示例：完整的 SmartAgent 全流程演示
展示如何把所有模块串联起来使用
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 80)
print("SmartAgent 完整流程演示")
print("=" * 80)

print("\n" + "=" * 80)
print("架构概览")
print("=" * 80)
print("""
  ┌──────────────┐
  │   用户   │
  └─────┬────┘
        │
        ▼
  ┌─────────────────────────────────┐
  │      Core (Agent 层)        │
  │   CodeAgent/ToolCallingAgent  │
  └─────┬───────────────────┬───────┘
        │                   │
        ▼                   ▼
  ┌──────────┐         ┌──────────┐
  │  Tools   │         │  Memory  │
  └────┬─────┘         └────┬─────┘
        │                   │
        ▼                   │
  ┌──────────┐         │
  │  LLM     │         │
  └────┬─────┘         │
        │                   │
        ▼                   ▼
  ┌───────────────────────────────┐
  │          RAG 层              │
  │  (知识库/向量检索          │
  └───────────────────────────────┘
""")

print("\n" + "=" * 80)
print("全流程工作原理")
print("=" * 80)

print("\n1. 用户输入问题")
print("   ↓")
print("2. Agent 接收问题")
print("   ↓")
print("3. Memory 检索相关记忆")
print("   ↓")
print("4. RAG 检索知识库")
print("   ↓")
print("5. 结合上下文")
print("   ↓")
print("6. LLM 生成回答")
print("   ↓")
print("7. 使用 Tools")
print("   ↓")
print("8. 存储新记忆")
print("   ↓")
print("9. 返回最终答案")

print("\n" + "=" * 80)
print("实际代码示例（概念演示）")
print("=" * 80)

print("\n【代码结构：")
print("""
from smart_agent import CodeAgent
from smart_agent.rag import VectorStore, BgeEmbedding
from smart_agent.memory import MemoryManager
from smart_agent.tools import NoteTool, TerminalTool, PythonInterpreterTool

# 1. 初始化 RAG
vector_store = VectorStore(dim=1024)
embeddings = BgeEmbedding()

# 2. 初始化 Memory
memory_manager = MemoryManager()

# 3. 准备 Tools
tools = [
    NoteTool(),
    TerminalTool(),
    PythonInterpreterTool(),
]

# 4. 创建 Agent
agent = CodeAgent(
    tools=tools,
    # 集成 RAG 和 Memory
)

# 5. 运行！
result = agent.run("你的问题")
""")

print("\n" + "=" * 80)
print("各模块的协同工作")
print("=" * 80)

print("\n📚 RAG 模块的作用：")
print("   • 加载文档")
print("   • 向量化")
print("   • 向量检索")
print("   • 提供相关知识")

print("\n🧠 Memory 模块的作用：")
print("   • 记住对话历史")
print("   • 存储重要信息")
print("   • 检索过往记忆")
print("   • 长期记忆管理")

print("\n🔧 Tools 模块的作用：")
print("   • Python 执行")
print("   • 笔记管理")
print("   • 终端操作")
print("   • 网页浏览")

print("\n🤖 LLM 模块的作用：")
print("   • 理解问题")
print("   • 生成回答")
print("   • 调用工具")
print("   • 协调流程")

print("\n🎯 Core (Agent) 的作用：")
print("   • 协调所有模块")
print("   • 决定做计划")
print("   • 执行步骤")
print("   • 返回答案")

print("\n" + "=" * 80)
print("完整示例：RAG + Memory + Tools")
print("=" * 80)

print("\n假设场景：智能知识库问答助手")
print("""
工作流程：
1. 用户问：什么是 RAG？
   ↓
2. Memory：搜索记忆 - 有没有之前聊过相关内容？
   ↓
3. RAG：检索知识库 - 相关文档
   ↓
4. Tools：如果需要，执行代码
   ↓
5. LLM：综合所有信息
   ↓
6. Memory：记住这次对话
   ↓
7. 返回答案给用户
""")

print("\n" + "=" * 80)
print("🎉 总结")
print("=" * 80)
print("""
是的！所有模块可以完美串联起来使用！

✓ 既可以单独使用某个模块
✓ 也可以任意组合使用
✓ 更可以全部串起来用

这就是 SmartAgent 的灵活性和强大之处！
""")

print("\n" + "=" * 80)
