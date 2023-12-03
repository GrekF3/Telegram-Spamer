import asyncio
import json
import os
import platform
import sys
from tqdm import tqdm
import pyfiglet
from pyrogram import Client
from pyrogram.errors import FloodWait

from core import SpamerSettings

# Инициализация объекта настроек
settings = SpamerSettings()



# Версия приложения
app_version = '0.9'

# Генерация ASCII-арт заголовка
ascii_art = pyfiglet.figlet_format(f"GrekF3 SPAMER {app_version}", font="slant")
print(ascii_art)


# Инициализация клиента Pyrogram
app = Client(name=settings.phone, api_id=settings.api_id, api_hash=settings.api_hash, phone_number=settings.phone)

# Путь к файлу для сохранения чатов
file_path = "chats.json"


def clear_console():
    """Очистка консоли в зависимости от операционной системы"""
    system = platform.system()
    if system == "Windows":
        os.system("cls")
    elif system == "Linux" or system == "Darwin":
        os.system("clear")


def chat_dump(chats):
    """Сохранение чатов в файл"""
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(chats, json_file, ensure_ascii=False, indent=4)


async def load_chats_from_file():
    """Загрузка чатов из файла"""
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, "r", encoding="utf-8") as json_file:
            chats = json.load(json_file)
        return chats
    return []


async def spamer_bot(chats):
    """Логика спам-бота"""
    clear_console()
    print(pyfiglet.figlet_format("START", font="slant"))
    await asyncio.sleep(1)
    print(f"Чатов загружено: {len(chats)}")
    
    if len(chats) > 1:
        print('Начинаю спам')
        await asyncio.sleep(1)
        chats_size = len(chats)
        i = 1
        for chat in chats:
            print(f"Отправил сообщение в {chat.get('name')} || {i}/{chats_size}")
            i += 1
            await asyncio.sleep(int(settings.timeout))
    else:
        print("Чатов недостаточно для спама.")
        await asyncio.sleep(1.5)
        clear_console()
        print(ascii_art)
        await main()


async def update_base():
    """Обновление базы чатов"""
    async with app:
        chats = await load_chats_from_file()
        
        # Если чатов нет или они пустые:
        if not chats:
            with tqdm(total=len(chats), desc="Выгружаю чаты: ", unit=" чатов") as pbar:
                try:
                    async for dialog in app.get_dialogs():
                        if "SUPERGROUP" == dialog.chat.type.name:
                            dialog_id = dialog.chat.id
                            dialog_name = dialog.chat.title
                            chat = {
                                "id": dialog_id,
                                "name": dialog_name,
                            }
                            chats.append(chat)
                            pbar.update(1)
                    print("Сохраняю файл chats.json")
                    chat_dump(chats)
                    print(f"Всего групп выгружено: {len(chats)}")
                    pbar.close()
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                finally:
                    clear_console()
                    ascii_art = pyfiglet.figlet_format(f"GrekF3 SPAMER {app_version}", font="slant")
                    print(ascii_art)
                    await main()


async def main():
    """Основная функция"""
    chats = await load_chats_from_file()
    # Вывод опций меню
    options = [
        "1.Начать спам",
        f"2.Обновить базу || {len(chats)} диалогов загружено.",
        "3.Выход",
        f"\nЗадержка между запросами: {settings.timeout}"
    ]

    for option in options:
        print(option)

    choice = input("Выбор: ")

    if choice == '1':
        chats = await load_chats_from_file()
        await spamer_bot(chats=chats)
    elif choice == '2':
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            os.remove(file_path)
            clear_console()
            await update_base()
        else:
            clear_console()
            await update_base()
    elif choice == '3':
        sys.exit()
    else:
        print("Неверный выбор. Пожалуйста, выберите снова.")
        await main()


async def SettingsLoader():
    if settings.check_all_fields_filled():
        print('Настройки были загружены \n')
        print(f'Ваш Api_Id: {settings.api_id}')
        print(f'Ваш Api_Hash: {settings.api_hash}')
        print(f'Ваш Phone: {settings.phone} \n')
        print(f'Задержка между запросами: {int(settings.timeout)} \n')
        await asyncio.sleep(2)
        clear_console()
        print(ascii_art)
        await main()
    else:
        print('Настройки не были загружены. Проверьте файл settings.txt')
        await asyncio.sleep(2)
        sys.exit()

# Запуск основного цикла
loop = asyncio.get_event_loop()
task = asyncio.ensure_future(SettingsLoader())
loop.run_until_complete(task)
