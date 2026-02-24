from __future__ import annotations

import sqlite3
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Response, status
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




@app.get("/health")
def health() -> dict[str, str]:
    return {"Status": "OK"}
