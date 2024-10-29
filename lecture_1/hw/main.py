import json
import math

async def app(scope, receive, send):
    assert scope['type'] == 'http'

    # Получаем данные о запросе
    request_method = scope['method']
    path = scope['path']
    query_string = scope['query_string'].decode()

    # Парсим параметры запроса
    params = dict(x.split('=') for x in query_string.split('&') if '=' in x)

    # Факториал
    if path == "/factorial" and request_method == "GET":
        response = await handle_factorial(params)

    # Числа Фибоначчи
    elif path == "/fibonacci" and request_method == "GET":
        response = await handle_fibonacci(params)

    # Среднее значение
    elif path == "/mean" and request_method == "GET":
        response = await handle_mean(params)

    # Если путь не найден
    else:
        response = {"status": 404, "message": "Not Found"}
    
    # Формируем HTTP ответ
    await send({
        'type': 'http.response.start',
        'status': response.get("status", 200),
        'headers': [
            (b'content-type', b'application/json'),
        ]
    })

    await send({
        'type': 'http.response.body',
        'body': json.dumps(response).encode(),
    })

# Обработчики для каждой функции

async def handle_factorial(params):
    n = params.get('n')
    if n is None or not n.isdigit() or int(n) < 0:
        return {"status": 400, "message": "Invalid input. Please provide a non-negative integer."}
    
    n = int(n)
    try:
        result = math.factorial(n)
        return {"status": 200, "n": n, "factorial": result}
    except OverflowError:
        return {"status": 400, "message": "Number too large to compute factorial."}

async def handle_fibonacci(params):
    n = params.get('n')
    if n is None or not n.isdigit() or int(n) < 0:
        return {"status": 400, "message": "Invalid input. Please provide a non-negative integer."}
    
    n = int(n)
    fib_seq = [0, 1]
    while len(fib_seq) < n:
        fib_seq.append(fib_seq[-1] + fib_seq[-2])

    return {"status": 200, "n": n, "fibonacci": fib_seq[:n]}

async def handle_mean(params):
    numbers = params.get('numbers')
    if numbers is None:
        return {"status": 400, "message": "Please provide a comma-separated list of numbers."}
    
    try:
        num_list = [float(n) for n in numbers.split(",")]
        if not num_list:
            return {"status": 400, "message": "The list of numbers is empty."}
        mean_value = sum(num_list) / len(num_list)
        return {"status": 200, "numbers": num_list, "mean": mean_value}
    except ValueError:
        return {"status": 400, "message": "Invalid input. Ensure all values are numbers."}
