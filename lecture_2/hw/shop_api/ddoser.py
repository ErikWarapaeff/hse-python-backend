from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from faker import Faker
import random

faker = Faker()

def create_item():
    """Создаёт товар через API."""
    item_data = {
        "name": faker.word(),
        "price": round(random.uniform(10, 100), 2)
    }
    response = requests.post("http://localhost:8080/item/", json=item_data)
    print(f"Create item response: {response.status_code}")

def get_item():
    """Получает данные случайного товара по ID через API."""
    item_id = random.randint(1, 100)  # замените на актуальные ID товаров
    response = requests.get(f"http://localhost:8080/item/{item_id}")
    print(f"Get item response: {response.status_code}")

def update_item():
    """Обновляет товар через API."""
    item_id = random.randint(1, 100)  # замените на актуальные ID товаров
    updated_data = {
        "name": faker.word(),
        "price": round(random.uniform(10, 100), 2)
    }
    response = requests.put(f"http://localhost:8080/item/{item_id}", json=updated_data)
    print(f"Update item response: {response.status_code}")

def delete_item():
    """Удаляет товар через API."""
    item_id = random.randint(1, 100)  # замените на актуальные ID товаров
    response = requests.delete(f"http://localhost:8080/item/{item_id}")
    print(f"Delete item response: {response.status_code}")

def create_cart():
    """Создаёт корзину через API."""
    response = requests.post("http://localhost:8080/cart/")
    print(f"Create cart response: {response.status_code}")

def add_item_to_cart():
    """Добавляет товар в корзину через API."""
    cart_id = random.randint(1, 100)  # замените на актуальные ID корзин
    item_id = random.randint(1, 100)  # замените на актуальные ID товаров
    response = requests.post(f"http://localhost:8080/cart/{cart_id}/add/{item_id}")
    print(f"Add item to cart response: {response.status_code}")

if __name__ == "__main__":
    with ThreadPoolExecutor() as executor:
        futures = []

        # Запросы для работы с товарами
        for _ in range(10):
            futures.append(executor.submit(create_item))
            futures.append(executor.submit(get_item))
            futures.append(executor.submit(update_item))
            futures.append(executor.submit(delete_item))

        # Запросы для работы с корзинами
        for _ in range(10):
            futures.append(executor.submit(create_cart))
            futures.append(executor.submit(add_item_to_cart))

        for future in as_completed(futures):
            future.result()
