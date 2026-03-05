"""定义 smart_agent 的最底层工具协议和基类。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type


class Tool(ABC):
    """
    所有智能体工具的最底层抽象基类。
    
    该类不依赖任何业务逻辑，旨在提供统一的接口协议，彻底解决循环导入问题。
    """
    name: str  # 工具名称
    description: str  # 工具描述
    inputs: Dict[str, Any]  # 输入参数模式定义
    output_type: Any  # 输出类型

    def __init__(self, *args, **kwargs):
        # 允许在初始化时动态覆盖属性
        if "name" in kwargs:
            self.name = kwargs["name"]
        if "description" in kwargs:
            self.description = kwargs["description"]
        if "inputs" in kwargs:
            self.inputs = kwargs["inputs"]
        if "output_type" in kwargs:
            self.output_type = kwargs["output_type"]

    @abstractmethod
    def __call__(self, *args, **kwargs) -> Any:
        """执行工具的核心逻辑。"""
        pass

    def run(self, *args, **kwargs) -> Any:
        """兼容旧版的工具运行入口，支持字典型单参数解包。
        
        如果传入单个字典参数且无kwargs，则自动解包字典作为参数。
        """
        if len(args) == 1 and isinstance(args[0], dict) and not kwargs:
            return self.__call__(**args[0])
        return self.__call__(*args, **kwargs)

    def to_tool_calling_prompt(self) -> str:
        """生成用于智能体提示词的工具描述字符串。
        
        该方法必须在基类中定义，以确保所有工具在框架内一致。
        返回格式化的工具说明，包含名称、描述和输入参数。
        """
        inputs_desc = []
        if isinstance(self.inputs, dict):
            for n, info in self.inputs.items():
                if isinstance(info, dict):
                    type_str = info.get("type", "any")
                    desc_str = info.get("description", "")
                    inputs_desc.append(f"- {n} ({type_str}): {desc_str}")
        
        prompt = f"Tool: {self.name}\nDescription: {self.description}\nInputs:\n"
        if inputs_desc:
            prompt += "\n".join(inputs_desc)
        else:
            prompt += "None"
        return prompt

    def setup(self) -> None:
        """可选的初始化逻辑，用于异步加载或资源准备。"""
        pass

    @property
    def is_initialized(self) -> bool:
        """工具是否已完成初始化。"""
        return True
