# Сервис аутентификации и авторизации с JWT

Это высокопроизводительный API-сервис, реализующий систему регистрации пользователей, входа в систему и управления доступом с использованием пар JWT-токенов (Access и Refresh).

## Основные функции:

### 1. Регистрация:
- Валидация входных данных
- Хеширование паролей
- Автоматическая отправка email-уведомления после успешной регистрации (реализовано через задачу Celery)

### 2. Вход в систему:
- Проверка учетных данных (email и пароль)
- Генерация пары JWT-токенов при успешной аутентификации:
  - **Access Token**
  - **Refresh Token**

### 3. Обновление токенов:
- Эндпоинт для обновления пары токенов с использованием действительного Refresh Token

### 4. Защищённые эндпоинты:
- Механизм зависимости FastAPI, который валидирует Access Token и извлекает данные пользователя

### 5. Выход из системы:
- Возможность добавлять Refresh Token в "черный список" (blacklist)

## Технологический стек:

- **PostgreSQL** — основная база данных
- **FastAPI** — веб-фреймворк
- **SQLAlchemy** — ORM
- **Pydantic** — валидация данных
- **PyJWT** — работа с JWT
- **Pytest** — тестирование
- **Celery** — очередь задач
- **Redis** — брокер сообщений и кэш
- **Docker** — контейнеризация

## Архитектура и безопасность:

- **Асинхронные операции**: ключевые операции (API, запросы к базе данных, Redis) выполняются асинхронно для максимальной производительности
- **Фоновые задачи**: отправка email через Celery обрабатывается в фоне, что ускоряет ответы API
- **Хеширование паролей**: пароли никогда не хранятся в открытом виде, используется надежный алгоритм хеширования
- **Время жизни токенов**: короткое время действия Access Token минимизирует риски при компрометации
- **Ротация Refresh Token**: при обновлении токенов старый Refresh Token аннулируется, а выдается новый, что повышает

## Как запустить:

### 1. Создать .env файл и записать свои значения в переменные окружения
### 2. Запустить Redis:
```
docker run \
--name auth-redis \
--network auth-bridge-network \
-p 3333:6379 \
-d redis:7.2 
```
### 3. Запустить Postgres:
```
docker run \
--name auth-postgres \
--network auth-bridge-network \
-v auth-data:/app \
-p 5555:5432 \
-e POSTGRES_USER=auth_user \
-e POSTGRES_PASSWORD=password \
-e POSTGRES_DB=db_name \
-d postgres:17
```
### 4. Получаем SSL сертификат
- **Останавливаем работу nginx, запущенным в docker**
- **Скачиваем snapd и certbot**: 
sudo app-get install snapd certbot
- **Скачиваем nginx и запускаем его**: sudo apt-get install nginx | sudo systemctl start nginx 
- **Получаем ssl сертификат от certbot**: sudo certbot certonly --nginx. Не забываем при получении указать свой домен !!! 
- **Удаляем установленный nginx**: sudo apt-get purge nginx nginx-common
### 5. Запустить nginx:
```
docker run --name auth-nginx --volume ./nginx.conf:/etc/nginx/nginx.conf --volume /etc/letsencrypt:/etc/letsencrypt --volume /var/lib/letsencrypt:/var/lib/letsencrypt --network auth-bridge-network -d  -p 443:443 nginx
```
### 4. Запустить приложение:
```
docker compose build
docker build up
```
