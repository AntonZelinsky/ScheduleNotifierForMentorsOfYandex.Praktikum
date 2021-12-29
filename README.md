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

4. Применить миграции
```bash
$ alembic upgrade head
```

5. Запустить сервер
```bash
$ uvicorn app.main:app
```
или
```bash
$ python run.py
```

## Попробовать

#### [Воркспейс на Постмане](https://app.getpostman.com/join-team?invite_code=92ff1b61042fad2ea03d6a251d93e14e&ws=9ebf341f-05c1-4b85-acb7-a7d9992c5101)  

FastAPI - Swagger UI  
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  

### Важно!
При изменении структуры базы не забывайте создавать и применять миграции
```bash
$ alembic revision --message="NAME_MIGRATION" --autogenerate
$ alembic upgrade head
```

## Конфигурация проекта
Чтобы задать проекту нужную конфигурацию используйте переменную ```ENVIRONMENT```.
Доступные конфиги:
- ```development```
- ```test```
- ```production```

Валидирование всех переменных окружения проекта осуществляется через файл ```config.py```, находящемся в директории ```core/```.
Если какие-то перменные окружения не были вами заданы в .env файле - в проекте будут использованы значения, заданные в файле ```config.py```.

Для запука в бота в режиме ```development``` достаточно использовать пулинг.
```DOMAIN_ADDRESS``` вам может пригодиться только в режимах ```test``` и ```production```.

### Важно
Если вы добавляете или удаляете какую-то переменную окружения - обязательно отобразите эти изменения в файле config.py

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

## Appreciation
- [notion-sdk-py](https://github.com/ramnes/notion-sdk-py)
- [fastapi-utils](https://github.com/dmontagu/fastapi-utils)