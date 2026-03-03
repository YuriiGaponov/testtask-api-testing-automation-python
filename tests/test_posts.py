import pytest
import requests
from requests import Response
from http import HTTPStatus


class TestPosts:

    def test_get_posts(
            self,
            api_session: requests.Session,
            posts_endpoint: str
    ) -> None:
        response: Response = api_session.get(posts_endpoint)
        data = response.json()
        assert response.status_code == HTTPStatus.OK
        assert isinstance(data, list), (
            f'Эндпоинт /posts должен возвращать список постов, '
            f'тип возвращенных данных: {type(data)}'
        )
    
    @pytest.mark.parametrize(
        'id, status_code', 
        [(1, HTTPStatus.OK),
         (-1, HTTPStatus.NOT_FOUND)]
    )
    def test_get_post(
        self,
        api_session: requests.Session,
        id: int,
        status_code: int,
        posts_endpoint: str,
        post_required_fields: tuple
    ) -> None:
        response: Response = api_session.get(f'{posts_endpoint}/{id}')
        data = response.json()
        assert response.status_code == status_code
        if id == 1:
            assert isinstance(data, dict), (
                f'Эндпоинт /posts/{id} должен возвращать словарь,\n'
                f'тип возвращенных данных: {type(data)}.'
            )
            for field in post_required_fields:
                assert field in data, f'Поле "{field}" отсутствует в ответе для post_id={id}'

    def test_create_post(
            self,
            api_session: requests.Session,
            posts_endpoint: str,
            new_post: dict,
    ) -> None:
        response: Response = api_session.post(posts_endpoint, json=new_post)
        data: dict = response.json()

        assert response.status_code == HTTPStatus.CREATED
        for key, value in data.items():
                assert value ==  data[key], (
                     f'При создании поста в поле "{key}" передано значение "{value}"\n'
                     f'Значение поля "{key}" созданного поста: {data[key]}'
                )

    @pytest.mark.parametrize(
        'id, status_code', 
        [(1, HTTPStatus.OK),
         (-1, HTTPStatus.INTERNAL_SERVER_ERROR)]
    )
    def test_update_post(
        self,
        api_session: requests.Session,
        id: int,
        status_code: int,
        posts_endpoint: str,
        new_post: dict,
    ) -> None:
        response: Response = api_session.put(f'{posts_endpoint}/{id}', json=new_post)
        assert response.status_code == status_code
        if id == 1:
            data: dict = response.json()
            for key, value in data.items():
                assert value ==  data[key], (
                     f'При обновлении поста post_id={id} в поле "{key}" передано значение "{value}"\n'
                     f'Обновленное значение поля "{key}": {data[key]}'
                )

    @pytest.mark.parametrize(
        'id, field, value',
        [(1, 'title', 'new_test_title'),
         (2, 'body', 'new_test_body'),
         (3, 'userId', 40000)]
    )
    def test_patch_post(
        self,
        api_session: requests.Session,
        id: int,
        field: str,
        value: str|int,
        posts_endpoint: str
    ) -> None:
        response: Response = api_session.patch(f'{posts_endpoint}/{id}', json={field: value})
        data: dict = response.json()
        assert response.status_code == HTTPStatus.OK
        assert value ==  data[field], (
            f'При обновлении поста post_id={id} в поле "{field}" передано значение "{value}"\n'
            f'Обновленное значение поля "{field}": {data[field]}'
        )

    def test_delete_post(
        self,
        api_session: requests.Session,
        posts_endpoint: str
    ) -> None:
        response: Response = api_session.delete(f'{posts_endpoint}/1')
        assert response.status_code == HTTPStatus.OK
    