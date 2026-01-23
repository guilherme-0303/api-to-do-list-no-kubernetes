from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.models.todos import Todo
from app.schemas.todos import (
    TodoSchema,
    TodoResponse,
    TodoPatch,
)


router = APIRouter(prefix='/todos', tags=['todos'])


Session = Annotated[Session, Depends(get_session)]


@router.post('/', response_model=TodoResponse)
def create_todo(
    todo: TodoSchema, session: Session,
):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
    )

    print(db_todo)

    session.add(db_todo)

    session.commit()
    session.refresh(db_todo)

    return db_todo


@router.get('/', response_model=list[TodoResponse])
def get_todos(session: Session):
    db_todos = session.query(Todo).all()

    if not db_todos:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Tasks not found.'
        )

    print(type(db_todos))

    return db_todos


@router.get('/{todo_id}', response_model=TodoResponse)
def get_todo(todo_id: UUID, session: Session):
    query = select(Todo).where(Todo.todo_id == todo_id)

    db_todo = session.scalar(query)

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found.'
        )

    return db_todo


@router.delete('/{todo_id}', response_model=TodoResponse)
def delete_todo(todo_id: UUID, session: Session):
    query = select(Todo).where(Todo.todo_id == todo_id)

    db_todo = session.scalar(query)

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found.'
        )

    session.delete(db_todo)
    session.commit()

    return db_todo


@router.patch('/{todo_id}', response_model=TodoResponse)
def patch_todo(todo_id: UUID, session: Session, todo: TodoPatch):
    query = select(Todo).where(Todo.todo_id == todo_id)

    db_todo = session.scalar(query)

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found.'
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo
