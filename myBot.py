"""
This is a send random wiki page and random image
"""
from bs4 import BeautifulSoup
import requests
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import filters
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import  Column, Integer, String
from sqlalchemy.orm import DeclarativeBase
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InputFile



engine = create_engine("postgresql://postgres:Hamachi2002@localhost/pythonDB")
class Base(DeclarativeBase): pass

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

Base.metadata.create_all(bind=engine)

class DataBaseName(StatesGroup):
    name = State()

class DataBaseDelete(StatesGroup):
    name = State()

API_TOKEN = '6191230429:AAHpMhWhUhVunl3XAGheFQRUNhvYDGXf3JU'


# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

buttonsText = [
                "Отправить случайную статью с вики", # Number - 0
                "База данных",                       # Number - 1
                "Отправить картинку"
                ]                       

                                                    # Acsess array
buttonsDataBaseText = [
                        "Добавить в базу данных",    # Number - 0
                        "Убрать из базы",            # Number - 1
                        "Показать базу",             # Number - 2
                        "Дропнуть базу (ОПАСНО и не работает)",    # Number - 3
                        "Обратно"
                        ]                   # Number - 4
keypad = [
        [types.KeyboardButton(text=buttonsDataBaseText[0])],
        [types.KeyboardButton(text=buttonsDataBaseText[1])],
        [types.KeyboardButton(text=buttonsDataBaseText[2])],
        [types.KeyboardButton(text=buttonsDataBaseText[3])],
        [types.KeyboardButton(text=buttonsDataBaseText[4])],
        
    ]

@dp.message_handler(lambda message: message.text == buttonsText[0])
async def send_random_article(message: types.Message):
    DataWikiPage = requests.get('https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%A1%D0%BB%D1%83%D1%87%D0%B0%D0%B9%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0')
    UpdatedText = BeautifulSoup(DataWikiPage.text, 'html.parser')
    print(UpdatedText)
    text = UpdatedText.find_all('p')
    textRet = ''
    for unit in text:
        print(unit.get_text())
        textRet = textRet + unit.get_text()
    await message.answer(textRet)


@dp.message_handler(lambda message: message.text == buttonsText[1])
async def database(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(keyboard=keypad, one_time_keyboard=True)
    await message.answer("База данных", reply_markup=keyboard)
    

@dp.message_handler(lambda message: message.text == buttonsText[2])
async def sendImage(message: types.Message):
    # URL-адрес изображения
    image_url = "https://cdn.donmai.us/sample/30/ab/__ueno_koyori_sayonara_wo_oshiete_drawn_by_amaai39__sample-30ab932eacff2fce7f76196c4792b48b.jpg"

    
    
    await bot.send_photo(message.chat.id, photo=image_url)
    


#
# Add to database
#

@dp.message_handler(lambda message: message.text == buttonsDataBaseText[0])
async def add_database(message: types.Message, state: FSMContext):

    print(message.text)
    keyboard = types.ReplyKeyboardMarkup(keyboard=keypad, one_time_keyboard=True)
    await message.answer("Имя, которое добавить в базу данных", reply_markup=keyboard)
    await DataBaseName.name.set()   
    #await state.update_data(username=message.text)
    
    #await state.finish()
    
    

@dp.message_handler(state=DataBaseName.name)
async def add_database_name(message: types.Message, state: FSMContext):
    # получение текстового ввода от пользователя
    name = message.text
    print(name)
    with Session(autoflush=False, bind=engine) as db:
        data = Users(name=name)
        db.add(data)     
        db.commit()     

    
    await message.answer(f"Вы добавляете имя {name} в базу данных.")

    
    await state.finish()
    
#
# Delete from database
#

@dp.message_handler(lambda message: message.text == buttonsDataBaseText[1])
async def delete_database(message: types.Message, state: FSMContext):

    keyboard = types.ReplyKeyboardMarkup(keyboard=keypad, one_time_keyboard=True)
    await message.answer("Имя, которое удалить из базы данных", reply_markup=keyboard)
    
    # Проверяем, что состояние не содержит имени для добавления в базу данных
    if await state.get_data() == {}:
        await state.finish()

    await DataBaseDelete.name.set()
    
# Определяем функцию обработчика для ввода имени
@dp.message_handler(state=DataBaseDelete.name)
async def process_delete(message: types.Message, state: FSMContext):
    # Получаем имя из сообщения
    name = message.text

    # Удаляем имя из базы данных
    with Session(autoflush=False, bind=engine) as db:
        user = db.query(Users).filter(Users.name==name).first()
        db.delete(user)  # удаляем объект
        db.commit()     # сохраняем изменения

    # Отправляем ответное сообщение
    await message.answer(f"Имя '{name}' удалено из базы данных")

    # Сбрасываем состояние
    await state.finish()    

    
#
# Show database
#

# хэндлер на текстовые сообщения, проверяем текст на соответствие второй кнопке
@dp.message_handler(lambda message: message.text == buttonsDataBaseText[2])
async def show_database(message: types.Message, state: FSMContext):
    textSend = ""
    with Session(autoflush=False, bind=engine) as db:
        # получение всех объектов
        users = db.query(Users).all()
        for p in users:
            print(f"{p.id}.{p.name}")
            textSend += str(p.id) + " : " + str(p.name) + "\n"
    keyboard = types.ReplyKeyboardMarkup(keyboard=keypad, one_time_keyboard=True)
    await message.answer(textSend, reply_markup=keyboard)



@dp.message_handler(lambda message: (message.text.startswith('/') == False) and message.text not in (buttonsText or buttonsDataBaseText))
async def send_welcome(message: types.Message):
    keypad = [
        [types.KeyboardButton(text=buttonsText[0])],
        [types.KeyboardButton(text=buttonsText[1])],
        [types.KeyboardButton(text=buttonsText[2])],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=keypad, one_time_keyboard=True)
    await message.reply("Хай я бот рандома, я могу тебе отправить либо случаную статью с вики, либо случайное Rule34 ^_^", reply_markup=keyboard)    
    
    
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
