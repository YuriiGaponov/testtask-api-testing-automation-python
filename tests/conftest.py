import pytest
import requests
from typing import Generator


BASE_URL: str = 'https://jsonplaceholder.typicode.com'

@pytest.fixture
def posts_endpoint() -> str:
    BASE_URL = 'https://jsonplaceholder.typicode.com'
    return f'{BASE_URL}/posts'

@pytest.fixture
def post_required_fields() -> tuple:
    return ('userId', 'id', 'title', 'body')

@pytest.fixture
def new_post() -> dict:
    return {
        "title": 'test_title',
        "body": 'test_body',
        "userId": 1
    }


@pytest.fixture(scope='function')
def api_session() -> Generator[requests.Session, None, None]:
    session = requests.Session()
    yield session
    session.close()
