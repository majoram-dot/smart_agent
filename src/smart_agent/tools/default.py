#!/usr/bin/env python
# coding=utf-8
"""
default_tools.py — 默认内置工具集。

提供基础的 Python 解释器工具、最终答案工具等。
`to_code_prompt` 方法统一由 `_BaseToolMixin` 提供，避免在每个类中重复实现。
"""
from dataclasses import dataclass

from ..executors.local_python import (
    BASE_BUILTIN_MODULES,
    MAX_EXECUTION_TIME_SECONDS,
    evaluate_python_code,
)


def __getattr__(name):
    if name == "Tool":
        from .core import Tool
        return Tool
    elif name == "PipelineTool":
        from .core import PipelineTool
        return PipelineTool
    elif name == "BaseTool":
        from .core import BaseTool
        return BaseTool
    raise AttributeError(f"module 'default_tools' has no attribute '{name}'")


@dataclass
class PreTool:
    name: str
    inputs: dict[str, str]
    output_type: type
    task: str
    description: str
    repo_id: str



# 已将 mixin 功能合并至 base.tool.Tool 基类


from ..base.tool import Tool

class PythonInterpreterTool(Tool):
    name = "python_interpreter"
    description = "This is a tool that evaluates python code. It can be used to perform calculations."
    inputs = {
        "code": {
            "type": "string",
            "description": "The python code to run in interpreter",
        }
    }
    output_type = "string"

    def __init__(self, *args, authorized_imports=None, timeout_seconds=MAX_EXECUTION_TIME_SECONDS, **kwargs):
        super().__init__(**kwargs)
        if authorized_imports is None:
            self.authorized_imports = list(set(BASE_BUILTIN_MODULES))
        else:
            self.authorized_imports = list(set(BASE_BUILTIN_MODULES) | set(authorized_imports))
        self.timeout_seconds = timeout_seconds
        self.executor = None

    def __call__(self, code: str) -> str:
        if self.executor is None:
            self.executor = LocalPythonExecutor(
                authorized_imports=self.authorized_imports,
                timeout_seconds=self.timeout_seconds,
            )
        output = self.executor(code)
        return output


class LocalPythonExecutor:
    def __init__(self, authorized_imports=None, timeout_seconds=MAX_EXECUTION_TIME_SECONDS):
        self.authorized_imports = authorized_imports or BASE_BUILTIN_MODULES
        self.timeout_seconds = timeout_seconds
        self.state = {}
        self.static_tools = {}

    def __call__(self, code: str):
        try:
            result, logs, is_final = evaluate_python_code(
                code,
                state=self.state,
                static_tools=self.static_tools,
                authorized_imports=self.authorized_imports,
            )
            return logs if logs else str(result)
        except Exception as e:
            return f"Error: {str(e)}"


TOOL_MAPPING = {
    "PythonInterpreterTool": PythonInterpreterTool,
}


class FinalAnswerTool(Tool):
    name = "final_answer"
    description = "Use this tool to provide the final answer to the user."
    inputs = {
        "answer": {
            "type": "string",
            "description": "The final answer to provide",
        }
    }
    output_type = "string"

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

    def __call__(self, answer: str) -> str:
        return answer
