## API Documentation

Swagger UI доступен по адресу: `/docs`  
Redoc доступен по адресу: `/redoc`

Примеры запросов:

```bash
# Добавление нового перевала
curl -X POST "http://your-host/submitData/" \
-H "Content-Type: application/json" \
-d '{
    "user": {
        "email": "user@example.com",
        "fam": "Иванов",
        "name": "Иван",
        "otc": "Иванович",
        "phone": "+79261234567"
    },
    "coords": {
        "latitude": 45.3842,
        "longitude": 7.1525,
        "height": 1200
    },
    "beauty_title": "пер. ",
    "title": "Перевал",
    "levels": {
        "winter": "1A",
        "summer": "1A",
        "autumn": "1A",
        "spring": "1A"
    },
    "images": [
        {
            "title": "Вид с перевала",
            "data": "base64-encoded-image-data"
        }
    ]
}'

# Получение данных о перевале
curl -X GET "http://your-host/submitData/1"

# Поиск по email пользователя
curl -X GET "http://your-host/submitData/?user__email=user@example.com"
```



## Запуск тестов

1. Установите тестовые зависимости:
```bash
pip install pytest
