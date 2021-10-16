#Квик старт

```bash
$ git clone git@github.com:AntonZelinsky/ScheduleNotifierForMentorsOfYandex.Praktikum.git
$ cd ScheduleNotifierForMentorsOfYandex.Praktikum
```

Создать и активировать виртуальное окружение  
подтянуть зависимости
```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

Добавить переменные окружения
```bash
$ mv .env.example .env
$ vim .env
```

Запустить докер-контейнер
```bash
$ docker-compose -f docker-compose.dev.yaml up -d
```

Запустить сервер
```bash
$ uvicorn app.main:app
```

Добавить юзера
```bash
$ curl -H "Content-Type: application/json" -d '{"telegram_id": 12345678, "name": "Full name"}' http://127.0.0.1:8000/users/
```

Добавить когорту
```bash
$ curl -H "Content-Type: application/json" -d '{"name": "20 когорта. Python-разработчик"}' http://127.0.0.1:8000/cohorts/
```

FastAPI - Swagger UI
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)


##Requirements
Протестировано на 
Docker 19.03
Docker-compose 1.29
Python 3.7