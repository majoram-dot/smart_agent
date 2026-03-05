# benchmarks/adapters/base_adapter.py
from abc import ABC, abstractmethod

class BaseEvalAdapter(ABC):
    """
    智能体评估适配器基类
    用于将特定格式的数据集记录(Record)转换为内部 Agent 的输入，
    并将 Agent 的非结构化/思维链输出转化为测试打分所需的数据结构。
    """
    
    def __init__(self, agent_instance):
        self.agent = agent_instance
        
    @abstractmethod
    def evaluate_record(self, record: dict) -> dict:
        """评估单条数据记录"""
        pass
