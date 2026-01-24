from http import HTTPStatus
from uuid import uuid4

from dataclasses import asdict

import factory
import pytest

from app.models.todos import Todo


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text', max_nb_chars=127)
    description = factory.Faker('text')


def test_create_todo(client):
    payload = {
        'title': 'Test todo',
        'description': 'Test todo description',
    }
        
    response = client.post(
        '/todos', json=payload,
    )
 
    expected_values = response.json().copy()
    expected_values.pop('todo_id')

    assert 'todo_id' in response.json()

    assert expected_values == {
        'title': 'Test todo',
        'description': 'Test todo description',
    }


def test_get_todos_should_return_5_todos(session, client):
    expected_todos = 5
    session.add_all(TodoFactory.create_batch(5))
    session.commit()

    response = client.get('/todos')

    print(response.json())

    assert len(response.json()) == expected_todos


def test_get_todos_error(session, client):
    response = client.get(f'/todos')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Tasks not found.'}


def test_get_todo(session, client):
    todo = TodoFactory()

    session.add(todo)
    session.commit()

    db_todo = session.query(Todo).one()
    
    response = client.get(f'/todos/{db_todo.todo_id}')

    response_json = response.json()
    expected_response = asdict(db_todo)

    assert response.status_code == HTTPStatus.OK
    assert response_json['title'] == expected_response['title']


def test_get_todo_error(session, client):
    random_uuid = uuid4()

    response = client.get(f'/todos/{random_uuid}')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


def test_delete_todo(session, client):
    todo = TodoFactory()

    session.add(todo)
    session.commit()

    db_todo = session.query(Todo).one()

    response = client.delete(f'/todos/{db_todo.todo_id}')

    response_json = response.json()
    expected_response = asdict(db_todo)

    assert response.status_code == HTTPStatus.OK
    assert response_json['title'] == expected_response['title']


def test_delete_todo_error(session, client):
    random_uuid = uuid4()

    response = client.delete(f'/todos/{random_uuid}')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


def test_patch_todo(session, client):
    todo = TodoFactory()

    session.add(todo)
    session.commit()

    db_todo = session.query(Todo).one()

    response = client.patch(
        f'/todos/{db_todo.todo_id}',
        json={'title': 'teste!'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'teste!'


def test_patch_todo_error(client):
    random_uuid = uuid4()

    response = client.patch(f'/todos/{random_uuid}', json={})

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}
