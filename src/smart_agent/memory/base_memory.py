from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class MemoryItem:
    id: str
    content: str
    memory_type: str
    importance: float = 0.5
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type,
            "importance": self.importance,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryItem":
        return cls(
            id=data["id"],
            content=data["content"],
            memory_type=data["memory_type"],
            importance=data.get("importance", 0.5),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
        )


class BaseMemory:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.memories: Dict[str, MemoryItem] = {}

    def add(self, content: str, importance: float = 0.5, **metadata) -> str:
        import uuid
        memory_id = str(uuid.uuid4())
        item = MemoryItem(
            id=memory_id,
            content=content,
            memory_type=self.__class__.__name__.lower().replace("memory", ""),
            importance=importance,
            metadata=metadata,
        )
        self.memories[memory_id] = item
        return memory_id

    def get(self, memory_id: str) -> Optional[MemoryItem]:
        return self.memories.get(memory_id)

    def search(self, query: str, limit: int = 10, min_importance: float = 0.0) -> List[MemoryItem]:
        results = []
        for item in self.memories.values():
            if item.importance >= min_importance:
                if query.lower() in item.content.lower():
                    results.append(item)
        results.sort(key=lambda x: (-x.importance, -x.timestamp.timestamp()))
        return results[:limit]

    def update(self, memory_id: str, content: Optional[str] = None, importance: Optional[float] = None, **metadata) -> bool:
        if memory_id not in self.memories:
            return False
        item = self.memories[memory_id]
        if content is not None:
            item.content = content
        if importance is not None:
            item.importance = importance
        if metadata:
            item.metadata.update(metadata)
        return True

    def remove(self, memory_id: str) -> bool:
        if memory_id in self.memories:
            del self.memories[memory_id]
            return True
        return False

    def get_all(self) -> List[MemoryItem]:
        return list(self.memories.values())

    def clear(self):
        self.memories.clear()

    def stats(self) -> Dict[str, Any]:
        return {
            "count": len(self.memories),
            "avg_importance": sum(m.importance for m in self.memories.values()) / len(self.memories) if self.memories else 0.0,
        }


class WorkingMemory(BaseMemory):
    def __init__(self, user_id: str, capacity: int = 50, ttl_minutes: int = 60):
        super().__init__(user_id)
        self.capacity = capacity
        self.ttl_minutes = ttl_minutes

    def add(self, content: str, importance: float = 0.5, **metadata) -> str:
        self._cleanup_expired()
        memory_id = super().add(content, importance, **metadata)
        self._enforce_capacity()
        return memory_id

    def _cleanup_expired(self):
        now = datetime.now()
        expired_ids = [
            mid for mid, item in self.memories.items()
            if (now - item.timestamp).total_seconds() > self.ttl_minutes * 60
        ]
        for mid in expired_ids:
            del self.memories[mid]

    def _enforce_capacity(self):
        if len(self.memories) > self.capacity:
            sorted_items = sorted(
                self.memories.values(),
                key=lambda x: (x.importance, x.timestamp.timestamp())
            )
            to_remove = sorted_items[:len(self.memories) - self.capacity]
            for item in to_remove:
                del self.memories[item.id]


class EpisodicMemory(BaseMemory):
    pass


class SemanticMemory(BaseMemory):
    pass


class PerceptualMemory(BaseMemory):
    pass
