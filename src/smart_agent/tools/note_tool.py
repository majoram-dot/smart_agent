import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Any

from ..base.tool import Tool

class NoteTool(Tool):
    name = "note_tool"
    description = "A note-taking tool that allows creating, reading, updating, searching, and deleting notes."
    inputs = {
        "action": {
            "type": "string",
            "description": "The action to perform: create, read, update, delete, search, list, summary"
        },
        "title": {
            "type": "string",
            "description": "Title of the note (for create/update)",
            "nullable": True
        },
        "content": {
            "type": "string",
            "description": "Content of the note (for create/update)",
            "nullable": True
        },
        "note_id": {
            "type": "string",
            "description": "ID of the note (for read/update/delete)",
            "nullable": True
        },
        "query": {
            "type": "string",
            "description": "Search query (for search)",
            "nullable": True
        },
        "note_type": {
            "type": "string",
            "description": "Type of note (for create/list)",
            "nullable": True
        },
        "tags": {
            "type": "array",
            "description": "Tags for the note (for create/update)",
            "nullable": True
        },
        "limit": {
            "type": "integer",
            "description": "Maximum number of results (for search/list)",
            "nullable": True
        }
    }
    output_type = "string"

    def __init__(self, workspace: str = "./notes"):
        super().__init__()
        self.workspace = Path(workspace)
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.notes_file = self.workspace / "notes.json"
        self._load_notes()

    def _load_notes(self):
        if self.notes_file.exists():
            with open(self.notes_file, "r", encoding="utf-8") as f:
                self.notes = json.load(f)
        else:
            self.notes = {}

    def _save_notes(self):
        with open(self.notes_file, "w", encoding="utf-8") as f:
            json.dump(self.notes, f, ensure_ascii=False, indent=2)

    def _generate_note_id(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"note_{timestamp}"

    def __call__(self, *args, **kwargs) -> Any:
        return self.forward(*args, **kwargs)

    def forward(self, action: str, title: Optional[str] = None, content: Optional[str] = None,
                note_id: Optional[str] = None, query: Optional[str] = None,
                note_type: Optional[str] = None, tags: Optional[List[str]] = None,
                limit: Optional[int] = 10) -> str:
        if action == "create":
            return self._create_note(title, content, note_type, tags)
        elif action == "read":
            return self._read_note(note_id)
        elif action == "update":
            return self._update_note(note_id, title, content, tags)
        elif action == "delete":
            return self._delete_note(note_id)
        elif action == "search":
            return self._search_notes(query, limit)
        elif action == "list":
            return self._list_notes(note_type, limit)
        elif action == "summary":
            return self._get_summary()
        else:
            return f"Unknown action: {action}. Valid actions: create, read, update, delete, search, list, summary"

    def _create_note(self, title: Optional[str], content: Optional[str],
                     note_type: Optional[str], tags: Optional[List[str]]) -> str:
        if not title or not content:
            return "Error: title and content are required for create action"

        note_id = self._generate_note_id()
        note = {
            "id": note_id,
            "title": title,
            "content": content,
            "type": note_type or "general",
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self.notes[note_id] = note
        self._save_notes()
        return f"Note created successfully!\nID: {note_id}\nTitle: {title}"

    def _read_note(self, note_id: Optional[str]) -> str:
        if not note_id:
            return "Error: note_id is required for read action"
        if note_id not in self.notes:
            return f"Error: Note with ID {note_id} not found"
        note = self.notes[note_id]
        return f"""Note Details:
ID: {note['id']}
Title: {note['title']}
Type: {note['type']}
Tags: {', '.join(note['tags'])}
Created: {note['created_at']}
Updated: {note['updated_at']}

Content:
{note['content']}"""

    def _update_note(self, note_id: Optional[str], title: Optional[str],
                     content: Optional[str], tags: Optional[List[str]]) -> str:
        if not note_id:
            return "Error: note_id is required for update action"
        if note_id not in self.notes:
            return f"Error: Note with ID {note_id} not found"
        note = self.notes[note_id]
        if title:
            note['title'] = title
        if content:
            note['content'] = content
        if tags is not None:
            note['tags'] = tags
        note['updated_at'] = datetime.now().isoformat()
        self._save_notes()
        return f"Note updated successfully!\nID: {note_id}"

    def _delete_note(self, note_id: Optional[str]) -> str:
        if not note_id:
            return "Error: note_id is required for delete action"
        if note_id not in self.notes:
            return f"Error: Note with ID {note_id} not found"
        note = self.notes.pop(note_id)
        self._save_notes()
        return f"Note deleted successfully!\nID: {note_id}\nTitle: {note['title']}"

    def _search_notes(self, query: Optional[str], limit: int) -> str:
        if not query:
            return "Error: query is required for search action"
        results = []
        query_lower = query.lower()
        for note_id, note in self.notes.items():
            if (query_lower in note['title'].lower() or
                query_lower in note['content'].lower() or
                any(query_lower in tag.lower() for tag in note['tags'])):
                results.append(note)
        results = results[:limit]
        if not results:
            return f"No notes found for query: {query}"
        output = f"Search Results ({len(results)} notes):\n\n"
        for i, note in enumerate(results, 1):
            output += f"{i}. [{note['id']}] {note['title']}\n"
            output += f"   Type: {note['type']}, Tags: {', '.join(note['tags'])}\n"
            output += f"   Preview: {note['content'][:100]}...\n\n"
        return output

    def _list_notes(self, note_type: Optional[str], limit: int) -> str:
        notes_list = list(self.notes.values())
        if note_type:
            notes_list = [n for n in notes_list if n['type'] == note_type]
        notes_list = notes_list[-limit:] if limit > 0 else notes_list
        notes_list.reverse()
        if not notes_list:
            return "No notes found"
        output = f"Notes ({len(notes_list)} notes):\n\n"
        for i, note in enumerate(notes_list, 1):
            output += f"{i}. [{note['id']}] {note['title']}\n"
            output += f"   Type: {note['type']}, Tags: {', '.join(note['tags'])}\n"
            output += f"   Created: {note['created_at'][:19]}\n\n"
        return output

    def _get_summary(self) -> str:
        total_notes = len(self.notes)
        if total_notes == 0:
            return "No notes in the system"
        type_counts = {}
        tag_counts = {}
        for note in self.notes.values():
            note_type = note['type']
            type_counts[note_type] = type_counts.get(note_type, 0) + 1
            for tag in note['tags']:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        output = "Notes Summary:\n\n"
        output += f"Total notes: {total_notes}\n\n"
        output += "By type:\n"
        for note_type, count in sorted(type_counts.items()):
            output += f"  - {note_type}: {count}\n"
        if tag_counts:
            output += "\nTop tags:\n"
            for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                output += f"  - {tag}: {count}\n"
        return output
