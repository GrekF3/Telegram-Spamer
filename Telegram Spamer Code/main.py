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
app_version = '1.0'

# Путь к файлу для сохранения чатов
file_path = "chats.json"

# Генерация ASCII-арт заголовка
ascii_art = pyfiglet.figlet_format(f"GrekF3 SPAMER {app_version}", font="slant")
print(ascii_art)

# Инициализация клиента Pyrogram
app = Client(name=settings.phone, api_id=settings.api_id, api_hash=settings.api_hash, phone_number=settings.phone)

def clear_console():
    """Очистка консоли в зависимости от операционной системы"""
    system = platform.system()
    if system == "Windows":
        os.system("cls")
    elif system == "Linux" or system == "Darwin":
        os.system("clear")

async def load_chats_from_file():
    """Загрузка чатов из файла"""
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, "r", encoding="utf-8") as json_file:
            chats = json.load(json_file)
        return chats
    return []

async def save_chats_to_file(chats, filename):
    """Сохранение чатов в файл с указанным именем"""
    with open(filename, "w", encoding="utf-8") as json_file:
        json.dump(chats, json_file, ensure_ascii=False, indent=4)

async def update_base():
    """Обновление базы чатов"""
    async with app:
        chats = await load_chats_from_file()
        
        if not chats:
            with tqdm(total=len(chats), desc="Выгружаю чаты: ", unit=" чатов") as pbar:
                try:
                    async for dialog in app.get_dialogs():
                        if "SUPERGROUP" == dialog.chat.type.name:
                            dialog_id = dialog.chat.id
                            dialog_name = dialog.chat.title
                            spam_text = 'Hello World'
                            chat = {
                                "id": dialog_id,
                                "name": dialog_name,
                                "spam_text": spam_text,
                            }
                            chats.append(chat)
                            pbar.update(1)
                    print("Сохраняю файл chats.json")
                    await save_chats_to_file(chats, filename='chats.json')
                    print(f"Всего групп выгружено: {len(chats)}")
                    pbar.close()
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                finally:
                    clear_console()
                    ascii_art = pyfiglet.figlet_format(f"GrekF3 SPAMER {app_version}", font="slant")
                    print(ascii_art)
                    await main()


async def find_chat_files():
    """Поиск JSON-файлов, содержащих 'chats' в названии"""
    chat_files = []
    for file in os.listdir():
        if file.endswith(".json") and "chats" in file.lower():
            chat_files.append(file)
    return chat_files

async def choose_chat_file():
    """Выбор JSON-файла с чатами"""
    chat_files = await find_chat_files()
    if not chat_files:
        print("Не найдено ни одного JSON-файла с чатами.")
        return None
    print("Найденные JSON-файлы с чатами:")
    for i, file in enumerate(chat_files):
        print(f"{i+1}. {file}")
    while True:
        try:
            choice = int(input("Выберите номер файла: "))
            if choice < 1 or choice > len(chat_files):
                raise ValueError
            return chat_files[choice - 1]
        except ValueError:
            print("Некорректный ввод. Пожалуйста, введите номер файла из списка.")

async def load_chats():
    """Загрузка чатов из выбранного файла JSON"""
    file_name = await choose_chat_file()
    if file_name:
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                chats = json.load(file)
            return chats
        except FileNotFoundError:
            print("Файл не найден.")
    return None

async def check_chat_access(chat):
    """Проверка доступности чата"""
    try:
        print(f"Проверка доступности чата \"{chat.get('name')}\"...")
        chat_info = await app.get_chat(chat.get('id'))  # Получение информации о чате
        await asyncio.sleep(1)
        if chat_info.permissions.can_send_messages:
            print(f"Чат \"{chat.get('name')}\" доступен для отправки сообщений.")
            return True
        else:
            print(f"Нет разрешения на отправку сообщений в чате \"{chat.get('name')}\".")
    except Exception as e:
        print(f"Ошибка доступа к чату \"{chat.get('name')}\": {e}")
    return False

async def spamer_bot():
    """Логика спам-бота"""
    chats = await load_chats()
    if chats:
        async with app:
            clear_console()
            print(pyfiglet.figlet_format("START", font="slant"))
            await asyncio.sleep(1)
            print(f"Чатов загружено: {len(chats)}")
            
            accessible_chats = [chat for chat in chats if await check_chat_access(chat)]
            if accessible_chats:
                print("Начинаю спам")
                not_sent_chats = []
                for i, chat in enumerate(accessible_chats, start=1):
                    print(f"{i}/{len(accessible_chats)}. Отправляю сообщение в чат: \"{chat.get('name')}\"")
                    chat_name = chat.get('name')
                    chat_text = chat.get('spam_text')
                    status = 'Жду отправки'
                    try:
                        await app.send_message(chat.get('id'), chat_text)  # Отправка сообщения в чат
                        status = 'Отправлено'
                    except Exception as e:
                        if "420 SLOWMODE_WAIT_X" in str(e):
                            status = "Ошибка отправки: Слишком много сообщений. Попробуйте позже."
                        else:
                            status = f'Ошибка отправки: {e}'
                        not_sent_chats.append((chat_name, status))  # Добавляем чат и причину ошибки в список неотправленных
                    print(f"Статус: {status}")
                    await asyncio.sleep(int(settings.timeout))
                
                print("Все сообщения отправлены")
                
                # Вывод списка чатов, в которые не было отправлено сообщение из-за ошибки
                if not_sent_chats:
                    print("Сообщения не отправлены в следующих чатах:")
                    for chat_name, error_reason in not_sent_chats:
                        print(f"{chat_name}: {error_reason}")
            else:
                print("Нет доступных чатов для отправки сообщений.")
    else:
        print("Невозможно загрузить чаты. Программа завершена.")


async def filter_chats_by_keyword(keyword):
    """Фильтрация чатов по ключевому слову"""
    chats = await load_chats_from_file()
    
    if not chats:
        print("Список чатов пуст. Пожалуйста, обновите базу чатов.")
        await asyncio.sleep(1.5)
        clear_console()
        print(ascii_art)
        await main()
        return
    
    filtered_chats = [chat for chat in chats if keyword.upper() in chat['name'].upper()]
    
    if not filtered_chats:
        print("Нет чатов, удовлетворяющих критериям.")
        await asyncio.sleep(1.5)
        while True:
            print("\nВыберите действие:")
            print("1. Выбрать другое ключевое слово")
            print("2. Вернуться в главное меню")
            
            choice = input("Введите номер действия: ")
            
            if choice == "1":
                keyword = input("Введите ключевое слово для фильтрации: ")
                await filter_chats_by_keyword(keyword)
                return
            elif choice == "2":
                clear_console()
                print(ascii_art)
                await main()
                return
            else:
                print("Некорректный ввод. Пожалуйста, выберите 1 или 2.")
    
    while True:
        for index, chat in enumerate(filtered_chats, start=1):
            print(f"{index}. {chat['name']} (ID: {chat['id']})")
            
        print("\n\nВыберите действие:")
        print("1. Вернуться в меню")
        print(f"2. Сохранить список {keyword}_chats.json")
        print("3. Удалить чат по номеру")
        
        choice = input("Введите номер действия: ")
        
        if choice == "1":
            clear_console()
            print(ascii_art)
            await main()
        elif choice == "2":
            clear_console()
            await save_chats_to_file(filtered_chats, f"{keyword}_chats.json")
            print(f"Список сохранен с названием {keyword}_chats.json")
            await asyncio.sleep(1)
            clear_console()
            await main()
            return
        elif choice == "3":
            try:
                index_to_remove = int(input("Введите номер чата для удаления: ")) - 1
                if 0 <= index_to_remove < len(filtered_chats):
                    del filtered_chats[index_to_remove]
                    print("Чат успешно удален.")
                else:
                    print("Некорректный номер чата.")
            except ValueError:
                print("Некорректный ввод. Пожалуйста, введите номер чата.")
        else:
            print("Некорректный ввод. Пожалуйста, выберите 1, 2 или 3.")
    

async def filtered_chats():
    """Вывод доступных чатов с возможностью фильтрации"""
    chats = await load_chats_from_file()
    
    if not chats:
        print("Список чатов пуст. Пожалуйста, обновите базу чатов.")
        await asyncio.sleep(1.5)
        clear_console()
        print(ascii_art)
        await main()
        return
    
    for index, chat in enumerate(chats, start=1):
        print(f"{index}. {chat['name']} (ID: {chat['id']})")
        
    print("\n\nВыберите действие:")
    print("1. Вернуться в меню")
    print("2. Отфильтровать чаты")
    
    choice = input("Введите номер действия: ")
    
    if choice == "1":
        await main()
    elif choice == "2":
        keyword = input("Введите ключевое слово для фильтрации: ")
        await filter_chats_by_keyword(keyword)
    else:
        print("Некорректный ввод. Пожалуйста, выберите 1 или 2.")
        await asyncio.sleep(1.5)
        clear_console()
        print(ascii_art)
        await main()

async def main():
    """Основная функция"""
    chats = await load_chats_from_file()
    # Вывод опций меню
    options = [
        "1.Начать спам",
        f"2.Обновить базу || {len(chats)} диалогов загружено.",
        "3.Доступные чаты (список) \n"
        "4.Выход",
        f"\nЗадержка между запросами: {settings.timeout}"
    ]

    for option in options:
        print(option)

    choice = input("Выбор: ")

    if choice == '1':
        await spamer_bot()
    elif choice == '2':
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            os.remove(file_path)
        await update_base()
    elif choice == '3':
        await filtered_chats()
    elif choice == '4':
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
