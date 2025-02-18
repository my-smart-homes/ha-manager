import pytest
from async_asgi_testclient import TestClient
from fastapi import status
from src.auth.dependencies import service
from src.auth import jwt
from datetime import datetime, timedelta
from uuid import UUID
import jose
from src.auth.jwt import create_access_token


@pytest.mark.asyncio
async def test_auth_user_tokens(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    # Mock the authenticate_user and create_refresh_token functions
    async def fake_authenticate_user(*args, **kwargs):
        # Use the same user created above
        return {"id": 1, "email": "email@fake.com"}

    async def fake_create_refresh_token(*args, **kwargs):
        return "fake_refresh_token"

    monkeypatch.setattr(service, "authenticate_user", fake_authenticate_user)
    monkeypatch.setattr(service, "create_refresh_token",
                        fake_create_refresh_token)

    # Use the registered user credentials to authenticate and get tokens
    resp = await client.post(
        "/auth/users/tokens",
        json={
            "email": "email@fake.com",
            "password": "123Aa!",

        },
    )
    resp_json = resp.json()
    print(resp_json)
    # Assert the response status and the presence of access and refresh tokens
    assert resp.status_code == status.HTTP_200_OK
    assert resp_json["success"] == True
    assert "access_token" in resp_json['data']
    assert "refresh_token" in resp_json['data']
    assert "expires_at" in resp_json['data']


@pytest.mark.asyncio
async def test_auth_user_refresh_tokens(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:

    async def fake_create_refresh_token(*args, **kwargs):
        return "fake_refresh_token"

    async def fake_expire_refresh_token(*args, **kwargs):
        pass

    async def fake_get_refresh_token(*args, **kwargs):

        return {'uuid': UUID('defcf1ec-0798-4651-bfb6-26267ebff6d8'), 'user_id': 1, 'refresh_token': 'fake_refresh_token', 'expires_at': datetime.utcnow()+timedelta(minutes=5), 'created_at': datetime(2024, 2, 13, 8, 27, 30, 576933), 'updated_at': None}

    def fake_create_access_token(*args, **kwargs):
        expiry_date = datetime.utcnow()+timedelta(minutes=5)
        jwt_data = {
            "sub": '1',
            "exp": expiry_date,
        }
        return jose.jwt.encode(jwt_data, 'SECRET', algorithm='HS256'), expiry_date

    async def fake_get_user_by_id(*args, **kwargs):
        return {"id": 1, "email": "email@fake.com"}

    monkeypatch.setattr(service, "create_refresh_token",
                        fake_create_refresh_token)
    monkeypatch.setattr(service, "expire_refresh_token",
                        fake_expire_refresh_token)
    monkeypatch.setattr(service, "get_refresh_token",
                        fake_get_refresh_token)
    monkeypatch.setattr(service, "get_user_by_id",
                        fake_get_user_by_id)
    monkeypatch.setattr(jwt, "create_access_token",
                        fake_create_access_token)

    # Use the registered user credentials to authenticate and get tokens
    resp = await client.put(
        "/auth/users/refresh-token",
        json={
            "refresh_token": "fake_refresh_token",
        },
    )
    resp_json = resp.json()
    print(resp_json)
    # Assert the response status and the presence of access and refresh tokens
    assert resp.status_code == status.HTTP_200_OK
    assert resp_json["success"] == True
    assert "access_token" in resp_json['data']
    assert "refresh_token" in resp_json['data']
    assert "expires_at" in resp_json['data']
