# benchmarks/adapters/bfcl_adapter.py
from .base_adapter import BaseEvalAdapter

class BFCLAdapter(BaseEvalAdapter):
    """
    用于桥接 SmartAgent 与 bfcl-eval 的评估适配器。
    
    工作流：
    1. 接收 BFCL 的函数库 json 与 Question。
    2. 将 BFCL Function Signatures 转化为 Agent 内置的 Tool。
    3. 调用 Agent 获取规划结论。
    4. 将 Agent Action 拦截并转译为 bfcl 要求的预测结果结构 `[{"name":"func","arguments":{...}}]`。
    """
    
    def evaluate_record(self, record: dict) -> dict:
        # TODO: 从 record 提取可用函数和 user prompt，组装并触发 self.agent
        # 拦截执行器并捕获模型所做出的函数调用抉择
        return {"prediction": "mock_bfcl_action"}
