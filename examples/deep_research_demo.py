"""重构后的深度研究演示脚本。"""

import os
import sys

# 自动处理路径：将 src 目录添加到 Python 搜索路径
# 这样无论在哪个目录下运行，都能正确导入 smart_agent
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, "..", "src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from smart_agent import run_deep_research, LiteLLMModel

def main():
    print("🚀 启动深度研究演示 (基于重构后的 clean 架构)")
    
    # 模拟研究课题
    topic = "2024年人工智能在大模型长上下文处理领域的技术突破与趋势"
    
    # 初始化模型（这步会自动加载环境变量中的 API Key）
    # 建议提前 set ANTHROPIC_API_KEY=xxx 或 OPENAI_API_KEY=xxx
    try:
        # 尝试从 .env 读取配置
        model_name = os.getenv("MODEL_NAME", "qwen-plus")
        api_base = os.getenv("OPENAI_BASE_URL")
        
        # 阿里云兼容模式通常需要加上 openai/ 前缀让 LiteLLM 识别
        if not model_name.startswith("openai/"):
            model_id = f"openai/{model_name}"
        else:
            model_id = model_name

        print(f"📡 正在初始化模型: {model_id}")
        model = LiteLLMModel(model_id=model_id, api_base=api_base)
        
        print(f"正在研究课题: {topic}")
        result = run_deep_research(topic, model=model)
        
        print("\n" + "="*50)
        print("✅ 研究完成！")
        print(f"研究摘要:\n{result.running_summary[:500]}...")
        print("="*50)
        
    except Exception as e:
        print(f"❌ 运行过程中发生错误 (可能是由于 API Key 未配置): {e}")
        print("\n提示：请确保已配置 ANTHROPIC_API_KEY 或 OPENAI_API_KEY。")

if __name__ == "__main__":
    main()
