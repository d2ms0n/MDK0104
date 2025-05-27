# 🚗 API для управления автомобилями

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-5ccb93?style=for-the-badge&logo=uvicorn&logoColor=white)

**RESTful API на FastAPI** для управления автопарком с полным набором CRUD-операций.

## 📚 Документация API

Интерактивная документация доступна по адресу:
- Swagger UI: `http://localhost:8000/docs`

## 🚀 Доступные эндпоинты

### 🚘 Операции с автомобилями

| Метод  | Эндпоинт       | Описание                     | Коды ответа |
|--------|----------------|-----------------------------|-------------|
| `GET`  | `/cars`        | Получить все автомобили      | 200         |
| `GET`  | `/cars/{id}`   | Получить конкретный автомобиль | 200, 404   |
| `POST` | `/cars`        | Добавить новый автомобиль     | 201, 400    |
| `PUT`  | `/cars/{id}`   | Обновить данные автомобиля    | 200, 404    |
| `DELETE` | `/cars/{id}` | Удалить автомобиль           | 204, 404    |



ПС У меня была заготовка прямо под это задание. Здесь https://github.com/d2ms0n/CarShop другая версия этого же задания. Ее хочу использовать в УП 01-02.
