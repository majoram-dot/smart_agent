# benchmarks/runners/run_bfcl.py
import argparse
import sys
import os

# 确保以可编辑模式运行或能找到包
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from benchmarks.adapters.bfcl_adapter import BFCLAdapter

def main():
    parser = argparse.ArgumentParser(description="Run BFCL Benchmark evaluation.")
    parser.add_argument("--model-name", type=str, default="qwen-plus", help="SmartAgent 使用的 LLM 模型名")
    parser.add_argument("--category", type=str, default="simple_python", help="测评数据集类别")
    
    args = parser.parse_args()
    print(f"[BFCL Runner] 初始化 {args.model_name} 的 SmartAgent...")
    
    # mock: from smart_agent.core.agents import ToolCallingAgent
    # agent = ToolCallingAgent(model_name=args.model_name)
    agent_mock = "MockAgentInstance"
    
    print("[BFCL Runner] 装载 Adapter...")
    adapter = BFCLAdapter(agent_mock)
    
    print(f"[BFCL Runner] 开始处理 {args.category} 数据集并由 Agent 进行预测...")
    # Mock records processing
    result = adapter.evaluate_record({"question": "mock question"})
    print(f"[BFCL Runner] 获取测试产物: {result}")
    
    print("[BFCL Runner] 评估执行完成。请查看 evaluation_results.jsonl。")

if __name__ == "__main__":
    main()
