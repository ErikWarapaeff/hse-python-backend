import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from lecture_4.demo_service.api.utils import initialize
from lecture_4.demo_service.api.users import router
from lecture_4.demo_service.core.users import UserInfo, UserRole, UserService, password_is_longer_than_8


@pytest.fixture(scope="module")
async def app():
    """Создание экземпляра FastAPI с маршрутизатором и инициализацией."""
    app = FastAPI()
    app.include_router(router)
    async with initialize(app):
        yield app


@pytest.fixture(scope="module")
def client(app):
    """Создание клиента тестирования."""
    return TestClient(app)


@pytest.fixture
def user_service(app):
    """Получение экземпляра UserService из приложения."""
    return app.state.user_service


@pytest.mark.asyncio
async def test_register_user(client):
    """Testing user registration."""
    response = await client.post("/register", json={
        "username": "testuser",
        "password": "validPassword123",
        "email": "test@example.com"
    })
    assert response.status_code == 201
    assert response.json()["detail"] == "User registered successfully."



@pytest.mark.asyncio
async def test_register_user_existing_username(client, user_service):
    """Тестирование регистрации с уже существующим именем пользователя."""
    user_service.register(UserInfo(
        username="existinguser",
        name="Existing User",
        birthdate="1990-01-01T00:00:00",
        role=UserRole.USER,
        password="validPassword123"
    ))

    response = client.post("/user-register", json={
        "username": "existinguser",
        "name": "Another User",
        "birthdate": "1995-05-05T00:00:00",
        "role": "user",
        "password": "anotherPassword123"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "username is already taken"


@pytest.mark.asyncio
async def test_register_user_short_password(client):
    """Тестирование регистрации с паролем менее 8 символов."""
    response = client.post("/user-register", json={
        "username": "shortpassworduser",
        "name": "Short Password User",
        "birthdate": "2000-01-01T00:00:00",
        "role": "user",
        "password": "short"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Password must be at least 8 characters long."


@pytest.mark.asyncio
async def test_register_user_missing_fields(client):
    """Тестирование регистрации без обязательных полей."""
    response = client.post("/user-register", json={
        "username": "incompleteuser",
        "role": "user",
        # Пропускаем имя и дату рождения
    })
    assert response.status_code == 422  # Unprocessable Entity
    assert "name" in response.json()["detail"][0]["loc"]
    assert "birthdate" in response.json()["detail"][0]["loc"]


@pytest.mark.asyncio
async def test_get_user_by_id(client, user_service):
    """Тестирование получения пользователя по ID."""
    user_info = UserInfo(
        username="user_id_test",
        name="User ID Test",
        birthdate="1995-01-01T00:00:00",
        role=UserRole.USER,
        password="password123"
    )
    entity = user_service.register(user_info)
    
    response = client.post("/user-get", params={"id": entity.uid})
    assert response.status_code == 200
    data = response.json()
    assert data['info']['username'] == "user_id_test"


@pytest.mark.asyncio
async def test_get_user_by_username(client, user_service):
    """Тестирование получения пользователя по имени пользователя."""
    user_info = UserInfo(
        username="user_username_test",
        name="User Username Test",
        birthdate="1995-01-01T00:00:00",
        role=UserRole.USER,
        password="password123"
    )
    entity = user_service.register(user_info)
    
    response = client.post("/user-get", params={"username": "user_username_test"})
    assert response.status_code == 200
    data = response.json()
    assert data['info']['username'] == "user_username_test"


@pytest.mark.asyncio
async def test_get_user_not_found(client):
    """Тестирование получения несуществующего пользователя по ID."""
    response = client.post("/user-get", params={"id": 999})  # Предполагая, что такого ID нет
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


@pytest.mark.asyncio
async def test_promote_user(client, user_service):
    """Тестирование повышения пользователя до админа."""
    user_info = UserInfo(
        username="user_promote_test",
        name="User Promote Test",
        birthdate="1995-01-01T00:00:00",
        role=UserRole.USER,
        password="password123"
    )
    entity = user_service.register(user_info)
    
    response = client.post("/user-promote", params={"id": entity.uid}, auth=("admin", "superSecretAdminPassword123"))
    assert response.status_code == 200

    # Проверка, что пользователь стал администратором
    assert user_service.get_by_id(entity.uid).info.role == UserRole.ADMIN


@pytest.mark.asyncio
async def test_promote_user_not_found(client, user_service):
    """Тестирование повышения несуществующего пользователя."""
    response = client.post("/user-promote", params={"id": 999}, auth=("admin", "superSecretAdminPassword123"))
    assert response.status_code == 400
    assert response.json()["detail"] == "user not found"


@pytest.mark.asyncio
async def test_authorization(client):
    """Тестирование авторизации."""
    response = client.post("/user-register", json={
        "username": "authuser",
        "name": "Auth User",
        "birthdate": "2000-01-01T00:00:00",
        "role": "user",
        "password": "authPassword123"
    })
    assert response.status_code == 200

    # Проверка авторизации
    response = client.post("/user-get", params={"username": "authuser"}, auth=("authuser", "authPassword123"))
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_authorization_invalid(client):
    """Тестирование невалидной авторизации."""
    response = client.post("/user-register", json={
        "username": "invalidauthuser",
        "name": "Invalid Auth User",
        "birthdate": "2000-01-01T00:00:00",
        "role": "user",
        "password": "authPassword123"
    })
    assert response.status_code == 200

    # Попытка авторизации с неверным паролем
    response = client.post("/user-get", params={"username": "invalidauthuser"}, auth=("invalidauthuser", "wrongPassword"))
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_user_info(client, user_service):
    """Тестирование обновления информации о пользователе."""
    user_info = UserInfo(
        username="user_update_test",
        name="User Update Test",
        birthdate="1995-01-01T00:00:00",
        role=UserRole.USER,
        password="password123"
    )
    entity = user_service.register(user_info)

    response = client.put("/user-update", params={
        "id": entity.uid,
        "name": "Updated User",
        "birthdate": "1990-01-01T00:00:00"
    })
    assert response.status_code == 200

    # Проверка обновления
    updated_user = user_service.get_by_id(entity.uid)
    assert updated_user.info.name == "Updated User"
    assert updated_user.info.birthdate == "1990-01-01T00:00:00"


@pytest.mark.asyncio
async def test_update_user_info_not_found(client):
    """Тестирование обновления информации о несуществующем пользователе."""
    response = client.put("/user-update", params={
        "id": 999,  # Не существующий ID
        "name": "Not Found User",
        "birthdate": "1990-01-01T00:00:00"
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


@pytest.mark.asyncio
async def test_delete_user(client, user_service):
    """Тестирование удаления пользователя."""
    user_info = UserInfo(
        username="user_delete_test",
        name="User Delete Test",
        birthdate="1995-01-01T00:00:00",
        role=UserRole.USER,
        password="password123"
    )
    entity = user_service.register(user_info)

    response = client.delete("/user-delete", params={"id": entity.uid})
    assert response.status_code == 200
    assert response.json()["detail"] == "User deleted successfully."

    # Проверка, что пользователь удалён
    with pytest.raises(KeyError):
        user_service.get_by_id(entity.uid)


@pytest.mark.asyncio
async def test_delete_user_not_found(client):
    """Тестирование удаления несуществующего пользователя."""
    response = client.delete("/user-delete", params={"id": 999})
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


@pytest.mark.asyncio
async def test_password_is_longer_than_8_valid():
    """Тестирование функции проверки пароля."""
    assert password_is_longer_than_8("validPassword123") is True


@pytest.mark.asyncio
async def test_password_is_longer_than_8_invalid():
    """Тестирование функции проверки пароля с невалидным паролем."""
    assert password_is_longer_than_8("short") is False

