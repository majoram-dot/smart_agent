from typing import Dict, List, Optional, Any
from .memory_manager import MemoryManager


class MemoryTool:
    def __init__(self, user_id: str, memory_types: Optional[List[str]] = None):
        self.memory_manager = MemoryManager(user_id, memory_types)
        self.memory_types = list(self.memory_manager.memory_types.keys())
    
    def run(self, params: Dict[str, Any]) -> Any:
        action = params.get("action")
        
        if action == "add":
            return self._add(params)
        elif action == "search":
            return self._search(params)
        elif action == "get":
            return self._get(params)
        elif action == "update":
            return self._update(params)
        elif action == "remove":
            return self._remove(params)
        elif action == "summary":
            return self._summary(params)
        elif action == "stats":
            return self._stats()
        elif action == "forget":
            return self._forget(params)
        elif action == "consolidate":
            return self._consolidate(params)
        elif action == "clear_all":
            return self._clear_all(params)
        else:
            return {"error": f"Unknown action: {action}"}
    
    def _add(self, params: Dict[str, Any]) -> Dict[str, Any]:
        content = params.get("content")
        if not content:
            return {"error": "content is required"}
        
        memory_type = params.get("memory_type", "working")
        importance = params.get("importance", 0.5)
        
        metadata = {k: v for k, v in params.items() if k not in ["action", "content", "memory_type", "importance"]}
        
        memory_id = self.memory_manager.add(content, memory_type, importance, **metadata)
        return {"success": True, "memory_id": memory_id}
    
    def _search(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        query = params.get("query", "")
        memory_type = params.get("memory_type")
        limit = params.get("limit", 10)
        min_importance = params.get("min_importance", 0.0)
        
        results = self.memory_manager.search(query, memory_type, limit, min_importance)
        return [item.to_dict() for item in results]
    
    def _get(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        memory_id = params.get("memory_id")
        if not memory_id:
            return {"error": "memory_id is required"}
        
        memory_type = params.get("memory_type")
        item = self.memory_manager.get(memory_id, memory_type)
        return item.to_dict() if item else None
    
    def _update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        memory_id = params.get("memory_id")
        if not memory_id:
            return {"error": "memory_id is required"}
        
        memory_type = params.get("memory_type")
        content = params.get("content")
        importance = params.get("importance")
        
        metadata = {k: v for k, v in params.items() if k not in ["action", "memory_id", "memory_type", "content", "importance"]}
        
        success = self.memory_manager.update(memory_id, memory_type, content, importance, **metadata)
        return {"success": success}
    
    def _remove(self, params: Dict[str, Any]) -> Dict[str, Any]:
        memory_id = params.get("memory_id")
        if not memory_id:
            return {"error": "memory_id is required"}
        
        memory_type = params.get("memory_type")
        success = self.memory_manager.remove(memory_id, memory_type)
        return {"success": success}
    
    def _summary(self, params: Dict[str, Any]) -> Dict[str, Any]:
        limit = params.get("limit", 10)
        return self.memory_manager.summary(limit)
    
    def _stats(self) -> Dict[str, Any]:
        return self.memory_manager.stats()
    
    def _forget(self, params: Dict[str, Any]) -> Dict[str, Any]:
        strategy = params.get("strategy", "importance_based")
        threshold = params.get("threshold", 0.2)
        memory_type = params.get("memory_type")
        return self.memory_manager.forget(strategy, threshold, memory_type)
    
    def _consolidate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        from_type = params.get("from_type")
        to_type = params.get("to_type")
        importance_threshold = params.get("importance_threshold", 0.6)
        
        if not from_type or not to_type:
            return {"error": "from_type and to_type are required"}
        
        return self.memory_manager.consolidate(from_type, to_type, importance_threshold)
    
    def _clear_all(self, params: Dict[str, Any]) -> Dict[str, Any]:
        memory_type = params.get("memory_type")
        self.memory_manager.clear_all(memory_type)
        return {"success": True}
