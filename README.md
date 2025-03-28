# Foodgram

Foodgram Best Recipe — это веб-приложение для публикации и поиска кулинарных рецептов.  

## Функциональность  
- Публикация рецептов с фото, ингридиентами и инструкцией.  
- Фильтрация по тегам (Easy, Difficult, Sweet и др.).  
- Добавление рецептов в избранное. 
- Формирование списка покупок.  
- Подписка на авторов.  
- API для работы с данными.  

## Роли пользователей
В проекте предусмотрены 4 роли пользователей:

1. Анонимный пользователь
    - Может просматривать рецепты и профиль автора рецепта.
    - Не может публиковать рецепты, подписываться или добавлять в избранное.

2. Зарегестрированный пользователь:
    - Может просматривать рецепты.
    - Может подписываться на авторов рецептов.
    - Может добавлять рецепты в избранное.
    - Может формировать список покупок.
    - Может публиковать и редактировать только свои рецепты.
3. Автор:
    - Все возможности зарегестрированного пользователя.
    - Может создавать, удалять и редактировать свои рецепты.
4. Администратор:
    - Полный доступ ко всем функциям проекта.
    - Управление пользователями, рецептами, ингредиентами и тегами через админ панель.

## Документация
**Полное описание API доступно после выполнения следующих шагов** :

1. Перейдите в каталог infra и выполните команду:

```bash
docker-compose up -d
```
Это запустит все необходимые сервисы, включая бэкенд и фронтенд.

2. Веб-интерфейс доступен по адресу:

    http://localhost

3. Документация API доступна по адресу:

    http://localhost/api/docs/


## Используемые технологии
- Python 3.9
- Django REST Framework
- PostgreSQL
- Docker

## Развертывание
1. Клонирование репозитория
```bash
git clone https://github.com/your-repo.git
cd your-repo
```
2. Запуск контейнеров
```bash
docker-compose up -d
```

3. Применение миграций и создание суперпользователя 
    docker exec -it foodgram_backend python manage.py migrate
    docker exec -it foodgram_backend python manage.py createsuperuser

4. Сборка статических файлов 
    docker exec -it foodgram_backend python manage.py collectstatic --noinput
    После выполнения всех шагов проект будет готов к использованию.

