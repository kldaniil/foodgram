«Фудграм» — это сайт, на котором можно публиковать собственные рецепты, 
добавлять чужие рецепты в избранное, подписываться на других авторов
и создавать список покупок для заданных блюд.

Проект доступен по адресу https://foodgram.kldaniil.ru

Инструменты и стек: 
#python #JSON #YAML #Django #React #API #Docker #Nginx #PostgreSQL #Gunicorn #JWT #Postman

Для запуска проекта на сервере:
загрузить в нужную директорию файл docker-compose.production.yml из репозитория.
Подготовить .env файл с константами, например -

    '''
    DB_TYPE=postgres
    POSTGRES_DB=db
    POSTGRES_USER=user
    POSTGRES_PASSWORD=password
    DB_HOST=db
    DB_PORT=5432
    SECRET_KEY='django-insecure-abc'
    DEBUG=True
    ALLOWED_HOSTS=127.0.0.1,localhost,mysite.ru
    '''

выполнить 

    '''
    sudo docker compose -f docker-compose.production.yml -d
    '''

в конфиге nginx пробросить запросы к сайту на 8003 порт.

Для запуска проекта локально в оркестре:
В терминале в папке проекта запустите выполните 

    '''
    sudo docker compose up -d
    '''

проект станет доступен по адресу http://localhost:8003/

Для запуска в виртуальном окружении:
Развернуть виртуальное окружение и установить зависимости:

    '''
    python3 -m venv venv
    source .venv/bin/activate
    python3 -m pip install --upgrade pip
    pip install -r requirements.txt
    python3 backend/manage.py migrate
    python3 backend/manage.py runserver
    '''

Установить Node js подходящим для вашей ОС способом.
В файле frontend/package.json в конце заменить "proxy": "http://web:8000/" на "proxy": "http://localhost:8000/"
Перейти в терминале в папку frontend,
выполнить npm install и npm start.

Для просмотра документации на API:
Перейти в директорию infra, выполнить

    '''
    sudo docker compose up -d
    '''
    
В браузере открыть http://localhost/api/docs/