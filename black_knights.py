"""Translate the Black Knights dashboard feed into VirtOffice agent records."""

from __future__ import annotations

import json
from pathlib import Path


HOME_BY_NAME = {
    "Lelouch": "meeting",
    "Diethard": "left",
    "Ohgi": "center",
    "Rakshata": "right",
    "Kallen": "right2",
    "Xingke": "left",
    "C.C.": "right2",
    "Tohdoh": "meeting",
    "Nunnally": "center",
}

EMOJI_BY_ROLE = {
    "Lead / Orchestrator": "♟",
    "Explorer": "⌕",
    "Architect": "⌘",
    "Rust/Audio Engineer": "◈",
    "Frontend Engineer": "✦",
    "Windows/Platform Engineer": "⚙",
    "Automated Test Engineer": "✓",
    "Reviewer": "◉",
    "UI/Manual QA Verifier": "◇",
    "Release Engineer": "↗",
}


def _agent_id(name: str) -> str:
    return "".join(character.lower() for character in name if character.isalnum())


def _assignments_for(name: str, tasks: list[dict]) -> list[tuple[dict, dict]]:
    assignments = []
    for task in tasks:
        for assignment in task.get("agents", []):
            if assignment.get("name") == name:
                assignments.append((task, assignment))
    return assignments


def build_black_knights_agents(roster: dict, tasks: list[dict]) -> list[dict]:
    """Build live 3D-office records from the dashboard's roster and task feed."""
    agents = []
    coffee_slot = 0

    for name, profile in roster.items():
        assignments = _assignments_for(name, tasks)
        active = [
            (task, assignment)
            for task, assignment in assignments
            if task.get("status") in {"in_progress", "blocked"}
            and assignment.get("status") != "done"
        ]
        completed = [
            (task, assignment)
            for task, assignment in assignments
            if task.get("status") == "done" or assignment.get("status") == "done"
        ]
        blocked = [pair for pair in active if pair[0].get("status") == "blocked"]

        if blocked:
            current_task, current_assignment = blocked[0]
            status = "away"
            home = HOME_BY_NAME.get(name, "center")
            task_label = f"Blocked — {current_task.get('title', 'Needs input')}"
        elif active:
            current_task, current_assignment = active[0]
            status = "working"
            home = HOME_BY_NAME.get(name, "center")
            task_label = current_task.get("title", "Working")
        else:
            current_assignment = {}
            status = "idle"
            home = f"coffee-{coffee_slot % 4}"
            coffee_slot += 1
            task_label = "Coffee break — no assigned task"

        active_count = len(active)
        output = [f"{active_count} active assignment{'s' if active_count != 1 else ''}"]
        output.extend(
            assignment.get("action", "")
            for _, assignment in active[:2]
            if assignment.get("action")
        )
        if not active:
            output.append("Available for the next mission")

        agents.append({
            "id": _agent_id(name),
            "name": name,
            "role": profile.get("role", "Black Knight"),
            "emoji": EMOJI_BY_ROLE.get(profile.get("role"), "♟"),
            "color": profile.get("color", "#8B5CF6"),
            "home": home,
            "status": status,
            "task": task_label,
            "tasks": [task.get("title", "Untitled task") for task, _ in active] or [task_label],
            "output": output,
            "stats": {"tasksDone": len(completed), "active": active_count, "hours": 0},
            "mood": 0.55 if blocked else (0.9 if active else 0.85),
            "typing": status == "working",
        })

    return agents


def load_black_knights_agents(dashboard_dir: str | Path) -> list[dict]:
    """Load the existing dashboard files without modifying them."""
    data_dir = Path(dashboard_dir) / "data"
    with (data_dir / "roster.json").open(encoding="utf-8") as roster_file:
        roster = json.load(roster_file)
    with (data_dir / "tasks.json").open(encoding="utf-8") as tasks_file:
        tasks = json.load(tasks_file).get("tasks", [])
    return build_black_knights_agents(roster, tasks)
