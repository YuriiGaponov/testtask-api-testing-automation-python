"""
Тесты для API эндпоинта /posts.

Проверяет основные CRUD‑операции:
- получение списка постов;
- получение поста по ID;
- создание нового поста;
- полное обновление поста (PUT);
- частичное обновление поста (PATCH);
- удаление поста.

Использует фикстуры из conftest.py:
- api_session: HTTP‑сессия с заголовками;
- posts_endpoint: базовый URL эндпоинта;
- new_post: тестовые данные для создания/обновления;
- post_required_fields: обязательные поля в ответе.
"""

import pytest
import requests
from requests import Response
from http import HTTPStatus


class TestPosts:
    """
    Набор тестов для эндпоинта /posts API.

    Включает проверки всех основных методов:
    GET (список и по ID), POST, PUT, PATCH, DELETE.
    """

    def _build_url(self, endpoint: str, post_id: int | None = None) -> str:
        """
        Формирует URL для запроса.

        Args:
            endpoint: базовый URL эндпоинта
            post_id: идентификатор поста (опционально)

        Returns:
            Сформированный URL (например, '/posts/1')
        """
        if post_id is not None:
            return f'{endpoint}/{post_id}'
        return endpoint
    
    def _assert_status(
        self, response: Response, expected_status: int
    ) -> None:
        """
        Проверяет статус‑код ответа.

        Args:
            response: объект ответа requests
            expected_status: ожидаемый HTTP‑статус

        Raises:
            AssertionError: если статус‑код не совпадает с ожидаемым
        """
        assert response.status_code == expected_status, (
            f'Ожидаемый статус {expected_status}, '
            f'получен {response.status_code}'
        )
    
    def _assert_json_type(
        self, response: Response, expected_type: type
    ) -> None:
        """
        Проверяет тип данных в JSON‑ответе.

        Args:
            response: объект ответа requests
            expected_type: ожидаемый тип (list, dict и т.п.)

        Raises:
            AssertionError: если тип данных не соответствует ожидаемому
        """
        data = response.json()
        assert isinstance(data, expected_type), (
            f'Ожидаемый тип {expected_type}, получен {type(data)}.'
        )
    
    def _assert_response_data(
            self, response: Response, expected_data: dict
    ) -> dict:
        """
        Сверяет данные в ответе с ожидаемыми значениями.

        Args:
            response: объект ответа requests
            expected_data: словарь с ожидаемыми полями и значениями

        Returns:
            Данные из ответа (dict)

        Raises:
            AssertionError: если какое‑либо поле не совпадает
        """
        data = response.json()
        for key, value in expected_data.items():
            assert data.get(key) == value, (
                f'Поле "{key}" не совпадает: '
                f'ожидаемо "{value}", получено "{data.get(key)}"'
            )
        return data

    def test_get_all_posts_returns_list(
        self, api_session: requests.Session, posts_endpoint: str
    ) -> None:
        """
        Тест: GET /posts возвращает список постов.

        Проверяет:
        - статус‑код 200;
        - тип ответа — список (list).
        """
        response: Response = api_session.get(self._build_url(posts_endpoint))
        self._assert_status(response, HTTPStatus.OK)
        self._assert_json_type(response, list)
    
    @pytest.mark.parametrize(
        'post_id, expected_status',
        [
            (1, HTTPStatus.OK),
            (-1, HTTPStatus.NOT_FOUND)
        ]
    )
    def test_get_post_by_id(
        self,
        api_session: requests.Session,
        post_id: int,
        expected_status: int,
        posts_endpoint: str,
        post_required_fields: tuple
    ) -> None:
        """
        Тест: GET /posts/{id} возвращает пост или ошибку.

        Для успешного ответа (200):
        - проверяет тип ответа (dict);
        - верифицирует наличие обязательных полей.

        Параметры параметризации:
            post_id: идентификатор поста
            expected_status: ожидаемый статус‑код
        """
        response: Response = api_session.get(
            self._build_url(posts_endpoint, post_id)
        )
        self._assert_status(response, expected_status)
        if expected_status == HTTPStatus.OK:
            self._assert_json_type(response, dict)
            data = response.json()
            for field in post_required_fields:
                assert field in data, f'Поле "{field}" отсутствует в ответе.'

    def test_create_post(
            self,
            api_session: requests.Session,
            posts_endpoint: str,
            new_post: dict,
    ) -> None:
        """
        Тест: POST /posts создаёт новый пост.

        Проверяет:
        - статус‑код 201 (CREATED);
        - соответствие возвращённых данных отправленным.
        """
        response: Response = api_session.post(
            self._build_url(posts_endpoint), json=new_post
        )
        self._assert_status(response, HTTPStatus.CREATED)
        self._assert_response_data(response, new_post)

    @pytest.mark.parametrize(
        'post_id, expected_status', 
        [
            (1, HTTPStatus.OK),
            (-1, HTTPStatus.NOT_FOUND)
        ]
    )
    def test_update_post_with_put(
        self,
        api_session: requests.Session,
        post_id: int,
        expected_status: int,
        posts_endpoint: str,
        new_post: dict,
    ) -> None:
        """
        Тест: PUT /posts/{id} полностью обновляет пост.

        Для успешного ответа (200):
        - сверяет возвращённые данные с отправленными.

        Параметры параметризации:
            post_id: идентификатор поста
            expected_status: ожидаемый статус‑код
        """
        response: Response = api_session.put(
            self._build_url(posts_endpoint, post_id), json=new_post
        )
        self._assert_status(response, expected_status)
        if expected_status == HTTPStatus.OK:
            self._assert_response_data(response, new_post)

    @pytest.mark.parametrize(
        'post_id, field, value, expected_status',
        [
            (1, 'title', 'new_test_title', HTTPStatus.OK),
            (1, 'body', 'new_test_body', HTTPStatus.OK),
            (1, 'userId', 40000, HTTPStatus.OK),
            (1, 'unexpected_field', 'unexpected_data', HTTPStatus.BAD_REQUEST),
            (-1, 'title', 'new_test_title', HTTPStatus.NOT_FOUND)
        ]
    )
    def test_partial_update_with_patch(
        self,
        api_session: requests.Session,
        post_id: int,
        field: str,
        value: str|int,
        expected_status: int,
        posts_endpoint: str
    ) -> None:
        """
        Тест: PATCH /posts/{id} частично обновляет пост.

        Для успешного ответа (200):
        - проверяет обновление указанного поля.

        Параметры параметризации:
            post_id: идентификатор поста
            field: имя поля для обновления
            value: новое значение поля
            expected_status: ожидаемый статус‑код
        """
        response: Response = api_session.patch(
            self._build_url(posts_endpoint, post_id), json={field: value}
        )
        self._assert_status(response, expected_status)

        if expected_status == HTTPStatus.OK:
            data: dict = response.json()
            assert data.get(field) == value, (
                f'Поле "{field}" не обновлено: '
                f'ожидаемо "{value}", получено "{data.get(field)}"'
            )

    @pytest.mark.parametrize(
        'post_id, expected_status', 
        [
            (1, HTTPStatus.NO_CONTENT),
            (-1, HTTPStatus.NOT_FOUND)
        ]
    )
    def test_delete_post(
        self,
        api_session: requests.Session,
        post_id: int,
        expected_status: int,
        posts_endpoint: str
    ) -> None:
        """
        Тест: DELETE /posts/{id} удаляет пост.

        Для успешного удаления (204 NO_CONTENT):
        - сервер не возвращает тело ответа (статус 204);
        - проверка ограничивается валидацией статус‑кода.

        Для несуществующего поста (404 NOT_FOUND):
        - проверяется возврат соответствующего статус‑кода.

        Параметры параметризации:
            post_id: идентификатор поста
            expected_status: ожидаемый статус‑код
        """
        response: Response = api_session.delete(
            self._build_url(posts_endpoint, post_id)
        )
        self._assert_status(response, expected_status)
    