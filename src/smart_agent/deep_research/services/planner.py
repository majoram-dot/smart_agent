"""负责将研究课题转化为可执行任务的服务。"""

from __future__ import annotations
import json
import logging
import re
from typing import Any, List, Optional

# 适配 smart_agent 的 BaseAgent 或相应类型
from ...llm.models import TodoItem, SummaryState
from ...llm.models import TodoItem, SummaryState
from ...prompts import get_current_date, todo_planner_instructions

logger = logging.getLogger(__name__)

TOOL_CALL_PATTERN = re.compile(
    r"\[TOOL_CALL:(?P<tool>[^:]+):(?P<body>[^\]]+)\]",
    re.IGNORECASE,
)

class PlanningService:
    """包装规划 Agent 以生成结构化的 TODO 项。"""

    def __init__(self, planner_agent: Any) -> None:
        self._agent = planner_agent

    def plan_todo_list(self, state: SummaryState) -> List[TodoItem]:
        """要求规划 Agent 将主题分解为可执行任务。"""

        prompt = todo_planner_instructions.format(
            current_date=get_current_date(),
            research_topic=state.research_topic,
        )

        # 适配 smart_agent 的 Agent 调用接口
        # 假设 _agent 是一个 smart_agent.core.BaseAgent 子类
        # 注意：此处输入不带上下文 content，因为是初始规划
        response = self._agent.run(prompt)
        # smart_agent 的 Agent 记忆管理略有不同，如需清除记忆可特殊处理
        
        logger.info("规划器原始输出 (截断): %s", str(response)[:500])

        tasks_payload = self._extract_tasks(str(response))
        todo_items: List[TodoItem] = []

        for idx, item in enumerate(tasks_payload, start=1):
            title = str(item.get("title") or f"任务{idx}").strip()
            intent = str(item.get("intent") or "聚焦主题的关键问题").strip()
            query = str(item.get("query") or state.research_topic).strip()

            if not query:
                query = state.research_topic

            task = TodoItem(
                id=idx,
                title=title,
                intent=intent,
                query=query,
            )
            todo_items.append(task)

        state.todo_items = todo_items

        titles = [task.title for task in todo_items]
        logger.info("规划器生成了 %d 个任务: %s", len(todo_items), titles)
        return todo_items

    @staticmethod
    def create_fallback_task(state: SummaryState) -> TodoItem:
        """规划失败时的保底任务。"""
        return TodoItem(
            id=1,
            title="基础背景梳理",
            intent="收集主题的核心背景与最新动态",
            query=f"{state.research_topic} 最新进展" if state.research_topic else "基础背景梳理",
        )

    def _extract_tasks(self, text: str) -> List[dict[str, Any]]:
        """将输出解析为任务字典列表。"""
        text = text.strip()
        
        # 简单移除可能的思考过程 (think tokens)
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)

        json_payload = self._extract_json_payload(text)
        tasks: List[dict[str, Any]] = []

        if isinstance(json_payload, dict):
            candidate = json_payload.get("tasks")
            if isinstance(candidate, list):
                for item in candidate:
                    if isinstance(item, dict):
                        tasks.append(item)
        elif isinstance(json_payload, list):
            for item in json_payload:
                if isinstance(item, dict):
                    tasks.append(item)

        return tasks

    def _extract_json_payload(self, text: str) -> Optional[dict[str, Any] | list]:
        """尝试从文本中定位并解析 JSON 对象或数组。"""
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = text[start : end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1 and end > start:
            candidate = text[start : end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                return None

        return None
