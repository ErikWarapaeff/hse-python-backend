import json
import math
from http import HTTPStatus
from typing import Any, Callable, Awaitable

async def app(
    scope: dict[str, Any],
    receive: Callable[[], Awaitable[dict[str, Any]]],
    send: Callable[[dict[str, Any]], Awaitable[None]],
) -> None:
    # Обрабатываем событие жизненного цикла ASGI (startup/shutdown)
    if scope["type"] == "lifespan":
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                return

    # Обработка HTTP запросов
    assert scope["type"] == "http"
    method = scope["method"]
    path = scope["path"]

    # Вспомогательная функция для отправки JSON ответа
    async def send_json_response(status: int, body: dict):
        await send({
            "type": "http.response.start",
            "status": status,
            "headers": [(b"content-type", b"application/json")]
        })
        await send({
            "type": "http.response.body",
            "body": json.dumps(body).encode("utf-8")
        })

    # Обработка /factorial? n=...
    if path == "/factorial" and method == "GET":
        query_string = scope.get("query_string", b"").decode("utf-8")
        query_params = dict(param.split("=") for param in query_string.split("&") if "=" in param)
        n = query_params.get("n")

        # Проверяем наличие параметра и его валидность
        if n is None or not n.lstrip("-").isdigit():
            await send_json_response(HTTPStatus.UNPROCESSABLE_ENTITY, {"detail": "Parameter 'n' is required and must be a valid integer."})
            return
        
        n = int(n)
        
        # Проверяем, что n не отрицательный
        if n < 0:
            await send_json_response(HTTPStatus.BAD_REQUEST, {"detail": "Invalid value for 'n', must be non-negative."})
            return
        
        # Вычисляем факториал
        result = math.factorial(n)
        await send_json_response(HTTPStatus.OK, {"result": result})

    # Обработка /fibonacci/{n}
    elif path.startswith("/fibonacci/") and method == "GET":
        try:
            n = int(path.split("/")[2])
        except (IndexError, ValueError):
            await send_json_response(HTTPStatus.UNPROCESSABLE_ENTITY, {"detail": "Path parameter 'n' must be a valid integer."})
            return

        if n < 0:
            await send_json_response(HTTPStatus.BAD_REQUEST, {"detail": "Invalid value for 'n', must be non-negative."})
            return

        # Вычисляем последовательность Фибоначчи
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        
        await send_json_response(HTTPStatus.OK, {"result": b})

    # Обработка /mean
    elif path == "/mean" and method == "GET":
        request = await receive()
        try:
            body = json.loads(request.get("body", b"").decode("utf-8"))
            if not isinstance(body, list) or not all(isinstance(i, (float, int)) for i in body):
                raise ValueError
        except ValueError:
            await send_json_response(HTTPStatus.UNPROCESSABLE_ENTITY, {"detail": "Request body must be a non-empty array of floats."})
            return

        if len(body) == 0:
            await send_json_response(HTTPStatus.BAD_REQUEST, {"detail": "Invalid value for body, must be a non-empty array of floats."})
            return

        # Вычисляем среднее арифметическое
        result = sum(body) / len(body)
        await send_json_response(HTTPStatus.OK, {"result": result})

    # Возвращаем 404 для неподдерживаемых путей
    else:
        await send({
            "type": "http.response.start",
            "status": HTTPStatus.NOT_FOUND,
            "headers": [(b"content-type", b"text/plain")]
        })
        await send({
            "type": "http.response.body",
            "body": b"404 Not Found"
        })
