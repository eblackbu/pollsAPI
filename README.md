# Тестовое задание - API для опросов
Задача: спроектировать и разработать API для системы опросов пользователей.

Функционал для администратора системы:

- авторизация в системе (регистрация не нужна) 
  <code> /api-auth/login либо /admin </code>
- добавление/изменение/удаление опросов. Атрибуты опроса: название, дата старта, дата окончания, описание. После создания поле "дата старта" у опроса менять нельзя
  <code> /api/v1/polls/poll </code>
- добавление/изменение/удаление вопросов в опросе. Атрибуты вопросов: текст вопроса, тип вопроса (ответ текстом, ответ с выбором одного варианта, ответ с выбором нескольких вариантов)
  <code> /admin/polls/question </code>

Функционал для пользователей системы:

- получение списка активных опросов:
  <code>GET /api/v1/polls/?active=True </code>
- прохождение опроса: 
  <code>POST /api/v1/completed_polls </code>
- получение пройденных пользователем опросов с детализацией по ответам (что выбрано) по ID уникальному пользователя
  <code>GET /api/v1/users/\<uuid\> </code>

Технологии: Django 2.2.10, Django REST framework.

## Запуск
  - С помощью docker-compose:  <br/>
    <code>
    $ docker-compose up </code>
  - Локально:  <br/>
    - <code>$ python3 -m venv venv </code>
    - <code>$ source venv/bin/activate </code>
    - <code>$(venv) pip install -r requirements.txt </code>  
    - <code>$(venv) python manage.py migrate </code>
    - <code>$(venv) python manage.py load_trash </code> 
    - <code>$(venv) python manage.py runserver <port\></code>