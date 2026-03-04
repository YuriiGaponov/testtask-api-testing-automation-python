"""
Набор фикстур для тестирования API сервиса постов.

Предоставляет:
- базовую HTTP‑сессию с предустановленными заголовками;
- URL эндпоинта /posts;
- тестовые данные для создания поста;
- список обязательных полей ответа.

Используется в тестах модуля test_posts.
"""

import pytest
import requests
from typing import Generator, Dict, Tuple

# --- Настройки API ---
BASE_URL: str = "https://jsonplaceholder.typicode.com"

# --- Фикстуры ---

@pytest.fixture(scope="module")
def posts_endpoint() -> str:
    """
    Возвращает URL эндпоинта /posts.

    Scope: module — достаточно создать один раз на модуль тестов.
    """
    return f"{BASE_URL}/posts"


@pytest.fixture(scope="function")
def post_required_fields() -> Tuple[str, ...]:
    """
    Список обязательных полей поста в ответе API.

    Scope: function — позволяет переопределять в отдельных тестах при необходимости.
    """
    return ("userId", "id", "title", "body")


@pytest.fixture(scope="function")
def new_post() -> Dict[str, str | int]:
    """
    Пример данных для создания нового поста.

    Scope: function — можно модифицировать в тестах через параметризацию.
    """
    return {
        "title": "test_title",
        "body": "test_body",
        "userId": 1
    }


@pytest.fixture(scope="session")
def api_session() -> Generator[requests.Session, None, None]:
    """
    Создаёт HTTP‑сессию для всех тестов в сессии.

    Преимущества:
    - Повторное использование соединения (быстрее).
    - Централизованная настройка заголовков/аутентификации.

    Scope: session — достаточно одной сессии на весь запуск тестов.
    """
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        # Пример добавления авторизации (если нужно):
        # "Authorization": "Bearer your-token"
    })
    yield session
    session.close()