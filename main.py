from __future__ import annotations

from operator import indexOf
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, model_validator
from enum import Enum

DB_PATH = "tasks.db"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP code goes here ---
    print("App is starting up")
    init_db()

    yield # App running and handling requests here

    # --- SHUTDOWN - runs when server stops ---
    print("App is shutting down")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Status(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class UserTask(BaseModel):
    name: str
    description: str | None = None
    status: Status
    due_date: str | None = None

class UpdatedTask(BaseModel):
    name: str | None = None
    description: str | None = None
    status: Status | None = None
    due_date: str | None = None

    @model_validator(mode="after")
    def check_if_empty(self):
        if self.name is None and self.description is None and self.status is None and self.due_date is None:
            raise ValueError("Must update at least one field")
        return self

class ServerTask(BaseModel):
    id: int
    name: str
    description: str | None = None
    status: Status
    due_date: str | None = None
    created_at: str
    updated_at: str


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT "todo",
                due_date TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()

def get_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()

@app.get("/health")
def health() -> dict[str, str]:
    return {"Status": "OK"}

@app.post("/tasks")
def create_task(userTask: UserTask):
    now = get_timestamp()
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO tasks (name, description, status, due_date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
            (userTask.name, userTask.description, userTask.status.value, userTask.due_date, now, now)
        )
        task_id = int(cursor.lastrowid)
    return ServerTask(
        id=task_id,
        name=userTask.name,
        description=userTask.description,
        status=userTask.status,
        due_date=userTask.due_date,
        created_at=now,
        updated_at=now
    )


@app.get("/tasks")
def list_tasks(limit: int = Query(default=10, ge=1, le=50), offset: int = Query(default=0, ge=0)):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            """SELECT * FROM tasks LIMIT ? OFFSET ?""",
            (limit, offset)
        )
        tasks = []
        rows = cursor.fetchall()
        for row in rows:
            tasks.append(ServerTask.model_validate(dict(row)))
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            """SELECT * FROM tasks WHERE id = ?""",
            (task_id,)
        )
        data = cursor.fetchone()
        if data is None:
            raise HTTPException(status_code=404, detail="Task not found")
    return ServerTask.model_validate(dict(data))

@app.put("/tasks/{task_id}")
def update_task(task_id: int, updatedTask: UpdatedTask):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        fields = updatedTask.model_dump(exclude_unset=True)
        set_clause = ", ".join(f"{key} = ?" for key in fields.keys())
        now = get_timestamp()
        values = list(fields.values()) + [now] + [task_id]
        cursor = conn.execute(
            f"""UPDATE tasks SET {set_clause}, updated_at = ? WHERE id = ?""",
            values
        )
        if cursor.rowcount == 0: # UPDATE doesn't return rows, so I use cursor.rowcount to check how many rows are affected
            raise HTTPException(status_code=404, detail="The task you're trying to update doesn't exist")
        
        row = conn.execute(
            """SELECT * FROM tasks WHERE id = ?""",
            (task_id,)
        ).fetchone()
    return ServerTask.model_validate(dict(row))

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            """DELETE FROM tasks WHERE id = ?""",
            (task_id,)
        )
        if cursor.rowcount == 0: # DELETE doesn't return rows, so I use cursor.rowcount to check how many rows are affected
            raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")