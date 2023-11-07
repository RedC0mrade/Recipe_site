![Состояние проекта](https://github.com/RedC0mrade/foodgram-project-react/actions/workflows/main.yml/badge.svg)
# Проект Recipe site
![Логотип Foodgram](https://fodddgram.hopto.org/favicon.ico)

Добро пожаловать в репозиторий проекта Recipe site. Этот проект предназначен для обмена рецептами и помощи приготовления блюд.
Пользуясь данным проектом вы ножете создавать собственные рецепты, добавлять, понравившиеся рецепты, в избанное, подписываться 
на авторов, добавить рецепт в корзину и скачать список продуктов необходимых для приготовления этих блюд.

## Ссылка Репозиторий - [RedC0mrade](https://github.com/RedC0mrade/Recipe_site)

## Оглавление

- [О проекте](#о-проекте)
- [Основные особенности](#основные-особенности)
- [Использование](#использование)
  - [Локальное развертывание](#локальное-развертывание)
  - [Удаленное развертывание](#удаленное-развертывание)
- [Описание проекта](#описание-проекта)
- [Автор](#автор)
- [Используемые технологии](#используемые-технологии)

## О проекте

Recipe site - это проект, разработанный в рамках курса на Яндекс.Практикум. Он призван продемонстрировать новые технологии 
в веб-разработке и предоставить практический опыт создания полноценного веб-приложения.

## Основные особенности

- Аутентификация пользователей: Создавайте аккаунты или входите, чтобы получить доступ к платформе.
- Загрузка рецептов: Делитесь рецептами с сообществом.
- Социальное взаимодействие: Подписывайтесь на других пользователей, добавляйте из рецепты в избранное.
- Поиск и исследование: Находите и открывайте новые рецепты.
- Готовность к продакшну: Развертывайте приложение для публичного использования.

## Использование

### Локальное развертывание

Чтобы развернуть приложение Recipe site локально, следуйте этим шагам:

1. Клонируйте репозиторий на вашем локальном компьютере:

   ```bash
   git clone https://github.com/https://github.com/RedC0mrade/Recipe_site
   cd Recipe site
   py manage.py makemigrations
   py manage.py migrate
   py manage.py runscript my_script -v2
   py manage.py runserver

2. Установите зависимости для бэкенда и запустите сервер разработки:
   ```bash
   cd ../frontend
   npm install
   npm start
Откройте веб-браузер и перейдите по адресу http://127.0.0.1, чтобы взаимодействовать с локальной версией Recipe site.


### Удаленное развертывание
1. Подключитесь по SSH к удаленному серверу и перейдите в директорию проекта.
2. Чтобы развернуть foodgram на удаленном сервере, выполните следующие шаги:

   Подготовьте окружение на удаленном сервере с необходимым программным обеспечением (Docker, Docker Compose и т.д.).
3. Выполните команду fork, на своём аккаунте github из этого репозитория 
## Ссылка Репозиторий - [RedC0mrade](https://github.com/RedC0mrade/Recipe_site)
4. Клонируйте репозиторий на удаленном сервере:

   ```bash

   git clone https://github.com/ваше-имя/Recipe_site.git
   cd Recipe sitet
5. Выполните скачивание и развертывание продакшн версии:
```bash
   docker-compose -f docker-compose.production.yml pull
   docker-compose -f docker-compose.production.yml up -d
```
Установка миграций и сбор статики, заполнение базы ингредиентами, суперпользователя и тэгами произойдет в автоматическом режиме.
<span style="background-color: yellow; color: red;">Внимание</span>. Имя пользователя и пароль для суперпользователя __admin__, 
в целях безопастности, не забудьте сменить пароль 

6. Для успешного развертывания проекта необходимо в главной директории создать файл .env, где будут указаны следуюшие параметры:
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DB
- DB_HOST
- DB_PORT
- DB_NAME
- SECRET_KEY
- ALLOWED_HOSTS
- DEBUG

### Описание проекта
Kittygram - это платформа социальных медиа, где пользователи могут делиться и взаимодействовать с фотографиями кошек. Пользователи могут создавать аккаунты, загружать изображения, отмечать окрас и год рождения котиков.

### Автор
Проект foodgram был создан [RedC0mrade](https://github.com/redc0mrade).

### Используемые технологии
Проект использует ряд технологий, включая, но не ограничиваясь:

- Фронтенд: HTML, CSS, JavaScript, React
- Бэкенд: Python, Django, PostgreSQL, Django Rest Framework, Djoser
### Примечание 
Развертывание: Docker, Docker Compose
Пожалуйста, обратите внимание, что приведенный выше список представляет общий обзор, и фактические использованные технологии и инструменты могут различаться. Для получения более подробной информации ознакомьтесь с исходным кодом проекта и документацией.
