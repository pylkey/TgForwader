**Как запустить**

Используйте python 3.9 и выше . Создать виртуальное окружение, установить зависимости командой


`pip install Telethon fuzzywuzzy python-Levenshtein`

**Как использовать**

*Первый запуск*

Выполнить `python tg_forwarder.py` необходимо ввести  API ID and API Hash (взать из https://my.telegram.org/apps) и свой номер телефона. 

Скрипт покажет меню 

`Выберете опции (ввести цифру)`

`1. Список чатов`

`2. Пересылать сообщения`

При первом запуске нужно ввести `1` , после этого необходимо ввести код подтверждения из Телеграмма, после этого появится список чатов в вашем аккаунте и он сохранится в файле `chats_of_<your_phone_number>.txt` на этом скрипт завершит свою работу

*Пересылка сообщений*

Выполнить `python TgTorwarder.py`. Скрит покажет меню
`Выберете опции (ввести цифру)`

`1. Список чатов`

`2. Пересылать сообщения`

Введите `2` далее скрипт попросит ввести id чатов из которых необходимо вести пересылку сообщений (возьмите их из файла `chats_of_<your_phone_number>.txt`). Id чатов вводите через запятую. Далее необходимо указать чат в который необходимо пересылать сообщения. Далее, через запятую вводите слова, которые будут пересылаться, если в этих сообщениях встретится указанное слово.

Если хотите, чтобы пересылались все сообщения то оставте это пустым.

После этого начнется пересылка сообщения. 
