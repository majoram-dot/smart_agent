"""任务总结工具。"""

from __future__ import annotations
from collections.abc import Callable, Iterator
from typing import Tuple, Any

from ...llm.models import SummaryState, TodoItem

class SummarizationService:
    """处理任务总结。"""

    def __init__(
        self,
        summarizer_factory: Callable[[], Any],
    ) -> None:
        self._agent_factory = summarizer_factory

    def summarize_task(self, state: SummaryState, task: TodoItem, context: str) -> str:
        """使用总结 Agent 生成特定于任务的摘要。"""

        prompt = self._build_prompt(state, task, context)
        agent = self._agent_factory()
        
        # 适配 smart_agent 调用
        response = agent.run(prompt)
        
        summary_text = str(response).strip()
        # 简单清理
        import re
        summary_text = re.sub(r'<think>.*?</think>', '', summary_text, flags=re.DOTALL).strip()
        
        return summary_text or "暂无可用信息"

    def _build_prompt(self, state: SummaryState, task: TodoItem, context: str) -> str:
        """构建提示词。"""
        return (
            f"研究主题：{state.research_topic}\n"
            f"任务名称：{task.title}\n"
            f"任务目标：{task.intent}\n"
            f"检索查询：{task.query}\n"
            f"搜索上下文：\n{context}\n\n"
            "请返回一份面向用户的 Markdown 总结。"
        )
