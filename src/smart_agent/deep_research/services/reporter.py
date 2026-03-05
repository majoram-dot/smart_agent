"""将任务结果汇总为最终报告的服务。"""

from __future__ import annotations
import logging
import re
from typing import Any

from ...llm.models import SummaryState

logger = logging.getLogger(__name__)

class ReportingService:
    """生成最终的结构化报告。"""

    def __init__(self, report_agent: Any) -> None:
        self._agent = report_agent

    def generate_report(self, state: SummaryState) -> str:
        """根据已完成的任务生成结构化报告。"""

        tasks_block = []
        for task in state.todo_items:
            summary_block = task.summary or "暂无可用信息"
            sources_block = task.sources_summary or "暂无来源"
            tasks_block.append(
                f"### 任务 {task.id}: {task.title}\n"
                f"- 任务目标：{task.intent}\n"
                f"- 检索查询：{task.query}\n"
                f"- 执行状态：{task.status}\n"
                f"- 任务总结：\n{summary_block}\n"
                f"- 来源概览：\n{sources_block}\n"
            )

        prompt = (
            f"研究主题：{state.research_topic}\n"
            f"任务概览：\n{''.join(tasks_block)}\n"
            "请整合所有子任务信息，撰写一份结构化的深度研究报告。"
        )

        response = self._agent.run(prompt)
        
        report_text = str(response).strip()
        # 简单清理思考过程
        report_text = re.sub(r'<think>.*?</think>', '', report_text, flags=re.DOTALL).strip()

        return report_text or "报告生成失败，请检查输入。"
