"""
yzli/calendar — Routes FastAPI
Agenda et scheduler — tâches planifiées, crons, tâches récurrentes par agent.

Extracted from the monolith server.py
"""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
from pathlib import Path

_root = Path(__file__).parent.parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from core_v2.db import q, run, log_db
from core_v2.bus import bus

router = APIRouter(tags=["calendar"])


# ─── Models ───────────────────────────────────────────────────────────────────

class CalendarTaskIn(BaseModel):
    title: str = "Tâche"
    description: Optional[str] = None
    cron_expr: Optional[str] = None
    agent: str = "Nancy"
    status: str = "active"
    type: str = "cron"
    client_slug: Optional[str] = None
    project_slug: Optional[str] = None
    scheduled_at: Optional[str] = None


# ─── Routes ───────────────────────────────────────────────────────────────────

@router.get("/api/calendar")
def list_calendar(client_slug: Optional[str] = None):
    if client_slug:
        return q(
            "SELECT * FROM calendar_tasks WHERE client_slug=? ORDER BY scheduled_at",
            (client_slug,)
        )
    return q("SELECT * FROM calendar_tasks ORDER BY scheduled_at")


@router.post("/api/calendar", status_code=201)
async def create_calendar_task(task: CalendarTaskIn):
    lid = run(
        "INSERT INTO calendar_tasks (title, description, cron_expr, agent, status, type, client_slug, project_slug, scheduled_at) VALUES (?,?,?,?,?,?,?,?,?)",
        (
            task.title,
            task.description,
            task.cron_expr,
            task.agent,
            task.status,
            task.type,
            task.client_slug,
            task.project_slug,
            task.scheduled_at,
        )
    )
    row = q("SELECT * FROM calendar_tasks WHERE id=?", (lid,), one=True)
    await bus.emit("schedule.created", {"id": lid, "title": task.title}, "info")
    return row


@router.get("/api/calendar/{task_id}")
def get_calendar_task(task_id: int):
    row = q("SELECT * FROM calendar_tasks WHERE id=?", (task_id,), one=True)
    if not row:
        raise HTTPException(404, "Task not found")
    return row


@router.put("/api/calendar/{task_id}")
async def update_calendar_task(task_id: int, task: CalendarTaskIn):
    run(
        "UPDATE calendar_tasks SET title=?, description=?, cron_expr=?, agent=?, status=?, type=?, client_slug=?, project_slug=?, scheduled_at=? WHERE id=?",
        (task.title, task.description, task.cron_expr, task.agent, task.status,
         task.type, task.client_slug, task.project_slug, task.scheduled_at, task_id)
    )
    row = q("SELECT * FROM calendar_tasks WHERE id=?", (task_id,), one=True)
    await bus.emit("schedule.updated", {"id": task_id}, "info")
    return row


@router.delete("/api/calendar/{task_id}")
async def delete_calendar_task(task_id: int):
    run("DELETE FROM calendar_tasks WHERE id=?", (task_id,))
    await bus.emit("schedule.deleted", {"id": task_id}, "warn")
    return {"deleted": task_id}
