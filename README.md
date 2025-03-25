**Api Description:**
1. Сначала нужно зарегестрировать себя в /auth/register
2. Затем в /auth/login нужно будет залогиниться и получить Bearer token, который нам понадобится в дальнейшем

--------- 
*Далее работа с основной логикой:*
Ручки: 
- POST /links/shorten – создает короткую ссылку.
- GET /links/{short_code} – перенаправляет на оригинальный URL.
- DELETE /links/{short_code} – удаляет связь.
- PUT /links/{short_code} – обновляет URL 
- GET /links/{short_code}/stats - получение статы
- POST /links/shorten - Создание кастомных ссылок
- GET /links/search?original_url={url} - Поиск ссылки по оригинальному URL
- POST /links/shorten - Указание времени жизни ссылки

Авторизация:
- POST /auth/register - регистрация юзера
- POST /auth/login - авторизация

Примеры запросов:
- Создание шорт урла:
`curl --location '127.0.0.1:8000/links/shorten' \
--header 'Content-Type: application/json' \
--data '{
  "original_url": "https://vk.com/",
  "custom_alias": "first_vk_3"
}'`
- Получения ориганал урл по шорт урлу:
`curl --location '127.0.0.1:8000/nQMOjJ' \
--header 'Content-Type: application/json'`

Инструкция по запуску:
1) docker-compose up
2) подождали 15-20 сек и пишем docker restart fastapi_url_shortener (почему-то основной контейнер не дожидается пока поднимутся зависимости, поэтому так помогает сделать коннект)


Описание БД:
БД состоит из двух таблиц. Поля описаны в миграции