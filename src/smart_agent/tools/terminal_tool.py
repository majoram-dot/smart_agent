import os
import subprocess
import sys
from pathlib import Path

from ..base.tool import Tool


class TerminalTool(Tool):
    name = "terminal_tool"
    description = "A terminal tool that allows executing shell commands safely within a specified workspace."
    inputs = {
        "command": {
            "type": "string",
            "description": "The shell command to execute"
        }
    }
    output_type = "string"

    def __init__(self, workspace: str = "./", timeout: int = 30):
        super().__init__()
        self.workspace = Path(workspace).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.forbidden_commands = [
            "rm -rf", "rm -fr", "del /s", "rd /s",
            "format", "mkfs", ":(){ :|:& };:",
            "chmod 777", "chown root", "sudo", "su",
            "> /dev/sd", "dd if=", "wget", "curl",
            "nc -e", "bash -i", "python -c",
            "shutdown", "reboot", "halt", "poweroff"
        ]
        self.allowed_commands = [
            "ls", "dir", "cd", "pwd", "echo", "cat", "type",
            "head", "tail", "grep", "find", "wc", "sort", "uniq",
            "python", "python3", "pip", "pip3",
            "git", "conda", "venv",
            "cp", "copy", "mv", "move", "mkdir", "md", "rmdir", "rd"
        ]

    def _is_safe_path(self, path: str) -> bool:
        try:
            target_path = Path(path).resolve()
            return self.workspace in target_path.parents or target_path == self.workspace
        except Exception:
            return False

    def _is_safe_command(self, command: str) -> tuple[bool, str]:
        command_lower = command.lower()
        
        for forbidden in self.forbidden_commands:
            if forbidden.lower() in command_lower:
                return False, f"Forbidden command pattern detected: {forbidden}"
        
        if ".." in command:
            parts = command.split()
            for part in parts:
                if ".." in part and not self._is_safe_path(part):
                    return False, "Path traversal attempt detected"
        
        if any(cmd in command_lower for cmd in ["rm", "del", "rd"]):
            return False, "Deletion commands are disabled for safety"
        
        return True, "Command is safe"

    def _prepare_command(self, command: str) -> tuple[str, dict]:
        env = os.environ.copy()
        cwd = str(self.workspace)
        
        if sys.platform == "win32":
            shell = True
            cmd = command
        else:
            shell = True
            cmd = command
        
        return cmd, {"cwd": cwd, "env": env, "shell": shell}

    def __call__(self, *args, **kwargs):
        return self.forward(*args, **kwargs)


    def forward(self, command: str) -> str:
        is_safe, message = self._is_safe_command(command)
        if not is_safe:
            return f"Security Error: {message}"
        
        try:
            cmd, kwargs = self._prepare_command(command)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                **kwargs
            )
            
            output_parts = []
            
            if result.stdout:
                output_parts.append(f"Stdout:\n{result.stdout}")
            
            if result.stderr:
                output_parts.append(f"Stderr:\n{result.stderr}")
            
            output_parts.append(f"Exit Code: {result.returncode}")
            
            return "\n".join(output_parts)
            
        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {self.timeout} seconds"
        except Exception as e:
            return f"Error executing command: {str(e)}"
