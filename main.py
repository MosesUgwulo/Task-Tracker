from __future__ import annotations

import os
import psycopg2
import psycopg2.extras
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timezone, date

from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, model_validator
from enum import Enum

POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "db")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "task_tracker_db")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "user")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "password")

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
    due_date: date | None = Field(default=None, description="Format: YYYY-MM-DD (e.g. 2026-03-17)")

class UpdatedTask(BaseModel):
    name: str | None = None
    description: str | None = None
    status: Status | None = None
    due_date: date | None = Field(default=None, description="Format: YYYY-MM-DD (e.g. 2026-03-17)")

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
    due_date: date | None = None
    created_at: str
    updated_at: str


@contextmanager
def get_connection():
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    ) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'todo',
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
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO tasks (name, description, status, due_date, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """,
            (userTask.name, userTask.description, userTask.status.value, userTask.due_date, now, now)
        )
        task_id = cursor.fetchone()[0]
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
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            """SELECT * FROM tasks LIMIT %s OFFSET %s""",
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
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            """SELECT * FROM tasks WHERE id = %s""",
            (task_id,)
        )
        data = cursor.fetchone()
        if data is None:
            raise HTTPException(status_code=404, detail="Task not found")
    return ServerTask.model_validate(dict(data))

@app.put("/tasks/{task_id}")
def update_task(task_id: int, updatedTask: UpdatedTask):
    with get_connection() as conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        fields = updatedTask.model_dump(exclude_unset=True)
        set_clause = ", ".join(f"{key} = %s" for key in fields.keys())
        now = get_timestamp()
        values = list(fields.values()) + [now] + [task_id]
        cursor.execute(
            f"""UPDATE tasks SET {set_clause}, updated_at = %s WHERE id = %s""",
            values
        )
        if cursor.rowcount == 0: # UPDATE doesn't return rows, so I use cursor.rowcount to check how many rows are affected
            raise HTTPException(status_code=404, detail="The task you're trying to update doesn't exist")
        
        cursor.execute(
            """SELECT * FROM tasks WHERE id = %s""",
            (task_id,)
        )
        row = cursor.fetchone()
    return ServerTask.model_validate(dict(row))

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """DELETE FROM tasks WHERE id = %s""",
            (task_id,)
        )
        if cursor.rowcount == 0: # DELETE doesn't return rows, so I use cursor.rowcount to check how many rows are affected
            raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")