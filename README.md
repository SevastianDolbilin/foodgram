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

## 📖 **Документация**  
Полное описание API доступно по адресу:  
📄 [foodgrambestrecipe.ddns.net/api/docs/](http://foodgrambestrecipe.ddns.net/api/docs/)  

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


