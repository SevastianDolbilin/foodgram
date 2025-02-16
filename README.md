# 🍽 **Foodgram Best Recipe**  

Foodgram Best Recipe — это веб-приложение для публикации и поиска кулинарных рецептов.  

## 🌍 **Размещение**  
Проект развернут и доступен по адресу:  
🔗 [foodgrambestrecipe.ddns.net](http://foodgrambestrecipe.ddns.net/)  

## 🚀 **Функциональность**  
- 📌 Публикация рецептов с фото, ингредиентами и инструкцией.  
- 🏷 Фильтрация по тегам (Easy, Difficult, Sweet и др.).  
- ⭐ Добавление рецептов в избранное.  
- 🛒 Формирование списка покупок.  
- 👥 Подписка на авторов.  
- 📡 API для работы с данными.  

## 🔐 **Роли пользователей**
В проекте предусмотрены 4 роли пользователей:

- 👤 Анонимный пользователь
    Может просматривать рецепты и профиль авторов.
    Не может публиковать рецепты, подписываться или добавлять в избранное.

- 🧑 Обычный пользователь (после регистрации и авторизации)
    Может просматривать рецепты.
    Может подписываться на авторов.
    Может добавлять рецепты в избранное.
    Может формировать список покупок.
    Может публиковать и редактировать только свои рецепты.
- ✍️ Автор (зарегистрированный пользователь, публикующий рецепты)
    Все возможности обычного пользователя.
    Может создавать, редактировать и удалять свои рецепты.
- 🛠 Администратор
    Полный доступ ко всем функциям проекта.
    Управление пользователями, рецептами и тегами через админ-панель

## 📖 **Документация**  
Полное описание API доступно по адресу:  
📄 Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу. 
 
По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.  

## 🛠 **Технологии**  
- Python 3.9  
- Django REST Framework  
- PostgreSQL  
- Docker  

## 📦 **Развертывание**  
1. Клонировать репозиторий:  
   ```bash
   git clone https://github.com/your-repo.git
   cd your-repo

2. Запустить приложение в Docker:
    docker-compose up -d


3. Применить миграции и создать суперпользователя:
    sudo docker exec -it foodgram_backend python manage.py migrate
    sudo docker exec -it foodgram_backend python manage.py createsuperuser

4. Собрать статику:
    sudo docker exec -it foodgram_backend python manage.py collectstatic --noinput


