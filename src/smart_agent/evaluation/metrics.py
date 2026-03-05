from abc import ABC, abstractmethod
from typing import Any, List, Dict

class Metric(ABC):
    """评估指标基类"""
    @abstractmethod
    def compute(self, predictions: List[Any], references: List[Any]) -> Dict[str, float]:
        pass

class AccuracyMetric(Metric):
    """准确率计算"""
    def compute(self, predictions: List[Any], references: List[Any]) -> Dict[str, float]:
        if not predictions:
            return {"accuracy": 0.0}
        correct = sum(1 for p, r in zip(predictions, references) if p == r)
        return {"accuracy": correct / len(predictions)}

class ExactMatchMetric(Metric):
    """精确匹配计算"""
    def compute(self, predictions: List[str], references: List[str]) -> Dict[str, float]:
        if not predictions:
            return {"exact_match": 0.0}
        correct = sum(1 for p, r in zip(predictions, references) if str(p).strip() == str(r).strip())
        return {"exact_match": correct / len(predictions)}
