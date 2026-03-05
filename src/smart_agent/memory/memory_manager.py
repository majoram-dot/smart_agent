from typing import Dict, List, Optional, Any
from .base_memory import (
    MemoryItem,
    BaseMemory,
    WorkingMemory,
    EpisodicMemory,
    SemanticMemory,
    PerceptualMemory,
)


class MemoryManager:
    def __init__(self, user_id: str, memory_types: Optional[List[str]] = None):
        self.user_id = user_id
        self.memory_types: Dict[str, BaseMemory] = {}
        
        if memory_types is None:
            memory_types = ["working", "episodic", "semantic", "perceptual"]
        
        self._init_memory_types(memory_types)
    
    def _init_memory_types(self, memory_types: List[str]):
        type_map = {
            "working": WorkingMemory,
            "episodic": EpisodicMemory,
            "semantic": SemanticMemory,
            "perceptual": PerceptualMemory,
        }
        
        for mem_type in memory_types:
            if mem_type in type_map:
                self.memory_types[mem_type] = type_map[mem_type](self.user_id)
    
    def add(self, content: str, memory_type: str = "working", importance: float = 0.5, **metadata) -> str:
        if memory_type not in self.memory_types:
            raise ValueError(f"Memory type '{memory_type}' not initialized")
        return self.memory_types[memory_type].add(content, importance, **metadata)
    
    def get(self, memory_id: str, memory_type: Optional[str] = None) -> Optional[MemoryItem]:
        if memory_type:
            if memory_type in self.memory_types:
                return self.memory_types[memory_type].get(memory_id)
            return None
        for mem in self.memory_types.values():
            item = mem.get(memory_id)
            if item:
                return item
        return None
    
    def search(self, query: str, memory_type: Optional[str] = None, limit: int = 10, min_importance: float = 0.0) -> List[MemoryItem]:
        results = []
        if memory_type:
            if memory_type in self.memory_types:
                results = self.memory_types[memory_type].search(query, limit, min_importance)
        else:
            for mem in self.memory_types.values():
                results.extend(mem.search(query, limit, min_importance))
            results.sort(key=lambda x: (-x.importance, -x.timestamp.timestamp()))
            results = results[:limit]
        return results
    
    def update(self, memory_id: str, memory_type: Optional[str] = None, content: Optional[str] = None, importance: Optional[float] = None, **metadata) -> bool:
        if memory_type:
            if memory_type in self.memory_types:
                return self.memory_types[memory_type].update(memory_id, content, importance, **metadata)
            return False
        for mem in self.memory_types.values():
            if mem.update(memory_id, content, importance, **metadata):
                return True
        return False
    
    def remove(self, memory_id: str, memory_type: Optional[str] = None) -> bool:
        if memory_type:
            if memory_type in self.memory_types:
                return self.memory_types[memory_type].remove(memory_id)
            return False
        for mem in self.memory_types.values():
            if mem.remove(memory_id):
                return True
        return False
    
    def forget(self, strategy: str = "importance_based", threshold: float = 0.2, memory_type: Optional[str] = None):
        targets = [self.memory_types[memory_type]] if memory_type and memory_type in self.memory_types else list(self.memory_types.values())
        removed = 0
        for mem in targets:
            items_to_remove = [item.id for item in mem.get_all() if item.importance < threshold]
            for mid in items_to_remove:
                mem.remove(mid)
                removed += 1
        return {"removed": removed, "strategy": strategy}
    
    def consolidate(self, from_type: str, to_type: str, importance_threshold: float = 0.6):
        if from_type not in self.memory_types or to_type not in self.memory_types:
            return {"consolidated": 0}
        from_mem = self.memory_types[from_type]
        to_mem = self.memory_types[to_type]
        consolidated = 0
        items_to_move = [item for item in from_mem.get_all() if item.importance >= importance_threshold]
        for item in items_to_move:
            to_mem.add(item.content, item.importance, **item.metadata)
            from_mem.remove(item.id)
            consolidated += 1
        return {"consolidated": consolidated, "from": from_type, "to": to_type}
    
    def get_all(self, memory_type: Optional[str] = None) -> List[MemoryItem]:
        if memory_type:
            if memory_type in self.memory_types:
                return self.memory_types[memory_type].get_all()
            return []
        all_items = []
        for mem in self.memory_types.values():
            all_items.extend(mem.get_all())
        return all_items
    
    def clear_all(self, memory_type: Optional[str] = None):
        if memory_type:
            if memory_type in self.memory_types:
                self.memory_types[memory_type].clear()
        else:
            for mem in self.memory_types.values():
                mem.clear()
    
    def summary(self, limit: int = 10) -> Dict[str, Any]:
        all_items = self.get_all()
        all_items.sort(key=lambda x: (-x.importance, -x.timestamp.timestamp()))
        return {
            "recent_memories": [item.to_dict() for item in all_items[:limit]],
            "total_count": len(all_items),
        }
    
    def stats(self) -> Dict[str, Any]:
        stats = {
            "user_id": self.user_id,
            "memory_types": {},
            "total_count": 0,
        }
        for mem_type, mem in self.memory_types.items():
            mem_stats = mem.stats()
            stats["memory_types"][mem_type] = mem_stats
            stats["total_count"] += mem_stats["count"]
        return stats
