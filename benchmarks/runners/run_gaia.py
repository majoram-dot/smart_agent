# benchmarks/runners/run_gaia.py
import argparse
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from benchmarks.adapters.gaia_adapter import GAIAAdapter

def main():
    parser = argparse.ArgumentParser(description="Run GAIA Benchmark evaluation.")
    parser.add_argument("--level", type=int, choices=[1, 2, 3], default=1, help="GAIA 难度级别")
    
    args = parser.parse_args()
    print(f"[GAIA Runner] 初始化多模态 SmartAgent 进行 Level {args.level} 测试...")
    
    # mock agent
    agent_mock = "MockAgentInstance"
    adapter = GAIAAdapter(agent_mock)
    
    print("[GAIA Runner] 注入复杂工具集合并投递数据集问题...")
    result = adapter.evaluate_record({"question": "mock task"})
    print(f"[GAIA Runner] 解析并提取出的单行 QEM 答案: {result}")
    
    print("[GAIA Runner] GAIA 评估轮次结束。")

if __name__ == "__main__":
    main()
