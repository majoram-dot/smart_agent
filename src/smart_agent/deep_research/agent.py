"""协调深度研究工作流的编排器。"""

from __future__ import annotations

import logging
from typing import Any, Callable
from threading import Lock

# 适配 smart_agent 的 Agent 实现
from ..agents.core import ToolCallingAgent
from ..llm.models import LiteLLMModel
from ..tools.note_tool import NoteTool
from ..tools.web_search import WebSearchTool

from .prompts import (
    report_writer_instructions,
    task_summarizer_instructions,
    todo_planner_system_prompt,
)
from ..llm.models import SummaryState, SummaryStateOutput, TodoItem
from .services.planner import PlanningService
from .services.reporter import ReportingService
from .services.search import dispatch_search, prepare_research_context
from .services.summarizer import SummarizationService

logger = logging.getLogger(__name__)

class DeepResearchAgent:
    """编排基于任务的研究工作流的核心类。"""

    def __init__(self, model: Any = None) -> None:
        """使用模型和工具初始化协调器。"""
        # 默认使用 LiteLLMModel，如果外部未提供
        self.model = model or LiteLLMModel()
        
        # 使用重构后的标准工具类
        self.note_tool = NoteTool()
        self.web_search_tool = WebSearchTool()
        
        # 重构后架构已天然支持协议，不再需要任何 ensure_tool_protocol 或补丁

        self._state_lock = Lock()

        # 创建各个阶段的专家 Agent
        self.todo_agent = ToolCallingAgent(
            tools=[self.note_tool, self.web_search_tool],
            model=self.model,
            instructions=todo_planner_system_prompt.strip(),
        )
        self.report_agent = ToolCallingAgent(
            tools=[self.note_tool],
            model=self.model,
            instructions=report_writer_instructions.strip(),
        )

        def factory():
            return ToolCallingAgent(
                tools=[self.note_tool],
                model=self.model,
                instructions=task_summarizer_instructions.strip(),
            )

        self._summarizer_factory: Callable[[], Any] = factory

        self.planner = PlanningService(self.todo_agent)
        self.summarizer = SummarizationService(self._summarizer_factory)
        self.reporting = ReportingService(self.report_agent)

    def run(self, topic: str) -> SummaryStateOutput:
        """执行研究流程并返回最终报告。"""
        state = SummaryState(research_topic=topic)
        
        logger.info(f"开始深度研究: {topic}")
        
        # 阶段 1: 规划
        state.todo_items = self.planner.plan_todo_list(state)

        if not state.todo_items:
            logger.info("未生成任务，使用保底策略")
            state.todo_items = [self.planner.create_fallback_task(state)]

        # 阶段 2: 执行子任务
        for task in state.todo_items:
            self._execute_task(state, task)

        # 阶段 3: 撰写报告
        report = self.reporting.generate_report(state)
        state.structured_report = report
        state.running_summary = report

        return SummaryStateOutput(
            running_summary=report,
            report_markdown=report,
            todo_items=state.todo_items,
        )

    def _execute_task(self, state: SummaryState, task: TodoItem) -> None:
        """为单个任务执行搜索 + 总结。"""
        task.status = "in_progress"
        logger.info(f"执行子任务: {task.title}")

        search_result, _ = dispatch_search(task.query, state.research_loop_count)

        if not search_result:
            task.status = "skipped"
            task.summary = "未发现搜索结果。"
            return

        sources_summary, context = prepare_research_context(search_result)
        task.sources_summary = sources_summary

        with self._state_lock:
            state.web_research_results.append(context)
            state.sources_gathered.append(sources_summary)
            state.research_loop_count += 1

        summary_text = self.summarizer.summarize_task(state, task, context)
        task.summary = summary_text.strip() if summary_text else "暂无可用信息"
        task.status = "completed"

def run_deep_research(topic: str, model: Any = None) -> SummaryStateOutput:
    """便捷调用函数。"""
    agent = DeepResearchAgent(model=model)
    return agent.run(topic)
