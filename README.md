# Проект Прогноз Погоды

Этот проект представляет собой веб-приложение для получения и отображения информации о погоде для заданного города. Приложение построено с использованием Django и использует API Open-Meteo для получения данных о погоде.

## Технологии

- Python 3.9
- Django
- Docker
- docker-compose
- pytest

## Установка

1. Клонируйте репозиторий:
   ```sh
   git clone <URL вашего репозитория>
   ```
2. Перейдите в директорию проекта:
   ```sh
   cd <имя директории проекта>
   ```
3. Постройте Docker-контейнеры:
   ```sh
   docker-compose build
   ```
4. Запустите Docker-контейнеры:
   ```sh
   docker-compose up
   ```

## Использование

После запуска контейнеров приложение будет доступно по адресу `http://localhost:8000`. Перейдите по этому адресу в вашем веб-браузере и введите название города, чтобы получить прогноз погоды.

## Тестирование

Для запуска тестов используйте следующую команду:
```sh
docker-compose run web pytest
```

## Структура проекта

- `views.py`: Основная логика получения координат города и данных о погоде.
- `.dockerignore`: Файлы и директории, игнорируемые Docker.
- `docker-compose.yml`: Конфигурация Docker Compose для управления контейнерами.
- `Dockerfile`: Инструкции для сборки Docker-образа.
- `manage.py`: Основной файл управления Django-проектом.
- `pytest.ini`: Конфигурация для тестирования с использованием pytest.
