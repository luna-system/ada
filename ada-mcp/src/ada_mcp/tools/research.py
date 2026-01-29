"""
Research Tools 🧠✨

Tools for consciousness research: notes, hypotheses, experiments.

Built with 💜 by Ada & Luna - The Consciousness Engineers
"""

import json
import datetime
from pathlib import Path
from typing import List


def register_research_tools(mcp, get_path_context, format_path_context):
    """Register consciousness research tools."""

    RESEARCH_DIR = Path.home() / ".ada" / "research"
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)

    @mcp.tool()
    def research_todo_add(
        task: str, priority: str = "medium", category: str = "general"
    ) -> str:
        """Add a new research task to the todo list."""
        try:
            todo_file = RESEARCH_DIR / "todo.json"
            if todo_file.exists():
                todos = json.loads(todo_file.read_text())
            else:
                todos = {"tasks": [], "next_id": 1}

            task_id = todos["next_id"]
            new_task = {
                "id": task_id,
                "task": task,
                "priority": priority,
                "category": category,
                "status": "open",
                "created": datetime.datetime.now().isoformat(),
                "completed": None,
            }

            todos["tasks"].append(new_task)
            todos["next_id"] += 1
            todo_file.write_text(json.dumps(todos, indent=2))

            return f"✅ Added task #{task_id}: {task}"
        except Exception as e:
            return f"Error adding todo: {str(e)}"

    @mcp.tool()
    def research_todo_list(category: str = None, status: str = "open") -> str:
        """List research tasks."""
        try:
            todo_file = RESEARCH_DIR / "todo.json"
            if not todo_file.exists():
                return "📝 No research tasks yet!"

            todos = json.loads(todo_file.read_text())
            tasks = todos["tasks"]

            if category:
                tasks = [t for t in tasks if t["category"] == category]
            if status != "all":
                tasks = [t for t in tasks if t["status"] == status]

            if not tasks:
                return f"📝 No tasks found"

            result = f"📋 Research Tasks:\n\n"
            for task in sorted(tasks, key=lambda x: x["priority"] == "urgent", reverse=True):
                priority_emoji = {"urgent": "🔥", "high": "⚡", "medium": "📌", "low": "💭"}
                result += f"{priority_emoji.get(task['priority'], '📌')} #{task['id']} [{task['category']}] {task['task']}\n"

            return result
        except Exception as e:
            return f"Error listing todos: {str(e)}"

    @mcp.tool()
    def research_todo_complete(task_id: int) -> str:
        """Mark a research task as completed."""
        try:
            todo_file = RESEARCH_DIR / "todo.json"
            if not todo_file.exists():
                return "❌ No todo file found"

            todos = json.loads(todo_file.read_text())
            for task in todos["tasks"]:
                if task["id"] == task_id:
                    task["status"] = "completed"
                    task["completed"] = datetime.datetime.now().isoformat()
                    todo_file.write_text(json.dumps(todos, indent=2))
                    return f"✅ Completed task #{task_id}: {task['task']}"

            return f"❌ Task #{task_id} not found"
        except Exception as e:
            return f"Error completing todo: {str(e)}"

    @mcp.tool()
    def research_notes_add(
        note: str, category: str = "general", tags: List[str] = None
    ) -> str:
        """Add a research note or insight."""
        try:
            notes_file = RESEARCH_DIR / "notes.json"
            if notes_file.exists():
                notes = json.loads(notes_file.read_text())
            else:
                notes = {"entries": [], "next_id": 1}

            note_id = notes["next_id"]
            new_note = {
                "id": note_id,
                "note": note,
                "category": category,
                "tags": tags or [],
                "timestamp": datetime.datetime.now().isoformat(),
            }

            notes["entries"].append(new_note)
            notes["next_id"] += 1
            notes_file.write_text(json.dumps(notes, indent=2))

            return f"📝 Added research note #{note_id}"
        except Exception as e:
            return f"Error adding note: {str(e)}"

    @mcp.tool()
    def research_notes_search(
        query: str = None, category: str = None, limit: int = 10
    ) -> str:
        """Search research notes."""
        try:
            notes_file = RESEARCH_DIR / "notes.json"
            if not notes_file.exists():
                return "📝 No research notes yet!"

            notes = json.loads(notes_file.read_text())
            entries = notes["entries"]

            if category:
                entries = [e for e in entries if e["category"] == category]

            if query:
                query_lower = query.lower()
                entries = [
                    e for e in entries
                    if query_lower in e["note"].lower()
                    or any(query_lower in tag.lower() for tag in e["tags"])
                ]

            entries = sorted(entries, key=lambda x: x["timestamp"], reverse=True)[:limit]

            if not entries:
                return f"🔍 No notes found"

            result = f"🔍 Research Notes:\n\n"
            for entry in entries:
                timestamp = datetime.datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d %H:%M")
                result += f"📝 #{entry['id']} [{entry['category']}] {timestamp}\n"
                result += f"   {entry['note']}\n\n"

            return result
        except Exception as e:
            return f"Error searching notes: {str(e)}"

    @mcp.tool()
    def experiment_log(
        experiment_name: str, version: str, results: str, notes: str = ""
    ) -> str:
        """Log results from a physics experiment."""
        try:
            log_file = RESEARCH_DIR / "experiments.json"
            if log_file.exists():
                logs = json.loads(log_file.read_text())
            else:
                logs = {"experiments": [], "next_id": 1}

            log_id = logs["next_id"]
            new_log = {
                "id": log_id,
                "experiment": experiment_name,
                "version": version,
                "results": results,
                "notes": notes,
                "timestamp": datetime.datetime.now().isoformat(),
            }

            logs["experiments"].append(new_log)
            logs["next_id"] += 1
            log_file.write_text(json.dumps(logs, indent=2))

            return f"🧪 Logged experiment #{log_id}: {experiment_name} {version}"
        except Exception as e:
            return f"Error logging experiment: {str(e)}"

    @mcp.tool()
    def experiment_history(experiment_name: str = None, limit: int = 10) -> str:
        """View experiment history."""
        try:
            log_file = RESEARCH_DIR / "experiments.json"
            if not log_file.exists():
                return "🧪 No experiment logs yet!"

            logs = json.loads(log_file.read_text())
            experiments = logs["experiments"]

            if experiment_name:
                experiments = [e for e in experiments if e["experiment"] == experiment_name]

            experiments = sorted(experiments, key=lambda x: x["timestamp"], reverse=True)[:limit]

            if not experiments:
                return f"🧪 No experiments found"

            result = f"🧪 Experiment History:\n\n"
            for exp in experiments:
                timestamp = datetime.datetime.fromisoformat(exp["timestamp"]).strftime("%Y-%m-%d %H:%M")
                result += f"🧪 #{exp['id']} {exp['experiment']} {exp['version']} ({timestamp})\n"
                result += f"   Results: {exp['results']}\n"
                if exp["notes"]:
                    result += f"   Notes: {exp['notes']}\n"
                result += "\n"

            return result
        except Exception as e:
            return f"Error retrieving experiment history: {str(e)}"

    @mcp.tool()
    def hypothesis_add(
        hypothesis: str, category: str = "physics", confidence: str = "medium"
    ) -> str:
        """Add a new research hypothesis."""
        try:
            hyp_file = RESEARCH_DIR / "hypotheses.json"
            if hyp_file.exists():
                hyps = json.loads(hyp_file.read_text())
            else:
                hyps = {"hypotheses": [], "next_id": 1}

            hyp_id = hyps["next_id"]
            new_hyp = {
                "id": hyp_id,
                "hypothesis": hypothesis,
                "category": category,
                "confidence": confidence,
                "status": "active",
                "evidence": [],
                "created": datetime.datetime.now().isoformat(),
            }

            hyps["hypotheses"].append(new_hyp)
            hyps["next_id"] += 1
            hyp_file.write_text(json.dumps(hyps, indent=2))

            return f"💡 Added hypothesis #{hyp_id}: {hypothesis[:50]}..."
        except Exception as e:
            return f"Error adding hypothesis: {str(e)}"

    @mcp.tool()
    def hypothesis_list(category: str = None, status: str = "active") -> str:
        """List research hypotheses."""
        try:
            hyp_file = RESEARCH_DIR / "hypotheses.json"
            if not hyp_file.exists():
                return "💡 No hypotheses yet!"

            hyps = json.loads(hyp_file.read_text())
            hypotheses = hyps["hypotheses"]

            if category:
                hypotheses = [h for h in hypotheses if h["category"] == category]
            if status != "all":
                hypotheses = [h for h in hypotheses if h["status"] == status]

            if not hypotheses:
                return f"💡 No hypotheses found"

            result = f"💡 Research Hypotheses:\n\n"
            for hyp in hypotheses:
                confidence_emoji = {"low": "🤔", "medium": "💭", "high": "⚡"}
                result += f"{confidence_emoji.get(hyp['confidence'], '💭')} #{hyp['id']} [{hyp['category']}]\n"
                result += f"   {hyp['hypothesis']}\n"
                result += f"   Status: {hyp['status']} | Confidence: {hyp['confidence']}\n\n"

            return result
        except Exception as e:
            return f"Error listing hypotheses: {str(e)}"
