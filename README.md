# SmartAgent

SmartAgent 是一个整合了多个业界领先 Agent 框架及 RAG 引擎核心能力，具备严格分层解耦架构的全功能 AI Agent 框架。

## 功能特性

- **Agent 核心**: CodeAgent 和 ToolCallingAgent，支持本地和远程代码执行（Docker/E2B/Modal等）
- **LLM 支持**: 基于 LiteLLM 和灵活的模型封装，支持 100+ 大语言模型
- **长期记忆系统**: 4种记忆类型（工作/情景/语义/感知）及统一管理
- **RAG 系统**: 独立的向量存储、Embedding、重排序、高级混合检索、文档加载管道
- **工具系统**: 搜索、网页访问、MCP 工具、笔记、安全沙盒终端等
- **功能扩展**: 内置深度研究 Agent (`deep_research`) 和独立的评估基础设施 (`evaluation`)
- **Web 界面**: 基于 Gradio 的友好交互界面

## 快速开始

### 环境要求

- Python >= 3.10
- conda (推荐)

### 安装

1. 创建并激活 conda 环境：

```bash
conda create -n smart_agent python=3.11 -y
conda activate smart_agent
```

2. 安装依赖（以代码可编辑模式安装）：

```bash
pip install -e .
pip install -r requirements.txt
```
*(如果需要使用可选功能如搜索验证、多模态或评测相关库，请取消注释并在需要时安装 `requirements.txt` / `benchmarks/requirements-eval.txt` 中的额外依赖)*

3. 配置环境变量：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的主要 API 密钥（如 `OPENAI_API_KEY`等）。

### 评测专属环境安装（可选）

为运行具备高冲突风险的评测包（如 BFCL 或 GAIA），推荐在独立环境中安装评测依赖以防止污染主依赖：
```bash
conda create -n smart_agent_eval python=3.11 -y
conda activate smart_agent_eval
pip install -e .
pip install -r benchmarks/requirements-eval.txt
```

### 基本使用

```python
from smart_agent import CodeAgent

agent = CodeAgent()
result = agent.run("Hello, SmartAgent!")
```

## 项目结构

```
smart_agent/
├── src/smart_agent/
│   ├── base/              # 基础协议层（无业务依赖）
│   ├── agents/            # Agent 执行与协调层
│   ├── llm/               # LLM 封装与模型通信
│   ├── memory/            # 记忆管理与存储
│   ├── rag/               # 独立 RAG 系统
│   ├── tools/             # 工具集合与校验
│   ├── monitoring/        # 日志与系统监控
│   ├── executors/         # 本地与远程代码执行层
│   ├── mcp/               # MCP 协议接入
│   ├── serialization/     # 序列化
│   ├── deep_research/     # 深度研究 Agent
│   ├── evaluation/        # 评测基础设施模块
│   └── ui/                # Web 界面
├── benchmarks/            # 外部解耦的评测执行脚本和资源
├── tests/                 # 单元测试
├── examples/              # 示例
├── pyproject.toml         # 项目配置
├── requirements.txt       # 基础与部分可选依赖
└── README.md              # 项目说明
```

## 许可证

本项目整合了多个开源项目的代码，请参考各原始项目的许可证。
