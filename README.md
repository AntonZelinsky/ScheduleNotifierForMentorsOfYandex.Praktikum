# Квик старт

```bash
$ git clone git@github.com:AntonZelinsky/ScheduleNotifierForMentorsOfYandex.Praktikum.git
$ cd ScheduleNotifierForMentorsOfYandex.Praktikum
```

1. Создать и активировать виртуальное окружение  
подтянуть зависимости
```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

2. Переименовать заготовку с переменными окружения.
```bash
$ mv .env.example .env
```
Добавить свои значения для переменных окружения

3. Запустить докер-контейнер.  
В докере поднимаем БД Postgres к которой можно подключится. 
Пропустите этот шаг, если будете использовать другую базу
```bash
$ docker-compose -f docker-compose.dev.yaml up -d
```

4. Запустить сервер
```bash
$ uvicorn app.main:app
```

## Тестировать

Добавить юзера, отправив удобным способом POST-запрос
```bash
$ curl -H "Content-Type: application/json" \
-d '{"telegram_id": 12345678, "name": "Full name"}' \
http://127.0.0.1:8000/users/
```

Добавить когорту, так же отправив POST-запрос любым доступным способом
```bash
$ curl -H "Content-Type: application/json" \
-d '{"name": "20 когорта. Python-разработчик"}' \
http://127.0.0.1:8000/cohorts/
```

FastAPI - Swagger UI  
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Локальный запуск бота через вебхуки (необходим установленный ngrok):
- запусти сервер ngrok
```bash
$ ./ngrok http 80
```
- скопируй https адрес, cозданный ngrok, в переменную DOMAIN_ADDRESS (.env файл)
Адрес должен выглядеть так: DOMAIN_ADDRESS=https://example.ngrok.io/BOT_TOKEN/telegramWebhook

- запусти бота из корневой директории приложения
```bash
$ python run.py
```

## Requirements
Протестировано на  
- Docker 19.03  
- Docker-compose 1.29  
- Python 3.7  
