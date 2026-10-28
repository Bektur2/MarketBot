
Запуск:

mac / linux:

python3 -m venv venv  
source venv/bin/activate  
python3 -m pip install -r requirements.txt  
cp .env.example .env  
python3 main.py

windows:

python -m venv venv  
venv\Scripts\activate  
python -m pip install -r requirements.txt  
copy .env.example .env  
python main.py

Перед запуском заполнить .env:
пока стоят мои данные 
BOT_TOKEN=  
SELLER_USERNAME=  
CHANNEL_URL=  
SUPPORT_USERNAME=  
PRODUCT_NAME=Название товара  
PRODUCT_PRICE=1500  
PRODUCT_AVAILABLE=true

SELLER_USERNAME и SUPPORT_USERNAME указывать без @.

Что есть в боте:

1. Витрина
2. Личный профиль
3. Вся информация
4. Пользователи сохраняются в SQLite
5. База создается автоматически

Если товар есть:

PRODUCT_AVAILABLE=true

Если товара нет:

PRODUCT_AVAILABLE=false

После изменения .env перезапустить бота