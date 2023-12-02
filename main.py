import asyncio
import json
import os
import platform
import sys
from tqdm import tqdm
import pyfiglet
from pyrogram import Client
from pyrogram.errors import FloodWait

app_version = 1.3
ascii_art = pyfiglet.figlet_format(f"GrekF3 SPAMER {app_version}", font="slant")
print(ascii_art)

api_id = '2110117'
api_hash = '3716da0d0d88a9317845ab7e20daf2a0'
app = Client('my_account', api_id=api_id, api_hash=api_hash)

file_path = "chats.json"


def clear_console():
    system = platform.system()
    if system == "Windows":
        os.system("cls")
    elif system == "Linux" or system == "Darwin":
        os.system("clear")


def chat_dump(chats):
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(chats, json_file, ensure_ascii=False, indent=4)


async def load_chats_from_file():
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, "r", encoding="utf-8") as json_file:
            chats = json.load(json_file)
        return chats
    return []


async def spamer_bot(chats):
    clear_console()
    print(pyfiglet.figlet_format("START", font="slant"))
    await asyncio.sleep(1)
    print(f"Чатов загружено: {len(chats)}")
    if len(chats) > 1:
        await asyncio.sleep(1)
        print('Начинаю спам')
        await asyncio.sleep(1)
        chats_size = len(chats)
        i = 1
        for chat in chats:
            print(
                f"Отправил сообщение в {chat.get('name')} || {i}/{chats_size}"
            )
            i += 1
            await asyncio.sleep(0.2)
    else:
        print("Чатов недостаточно для спама.")
        await main()


async def update_base():
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

    options = [
                "1.Начать спам",
                "2.Обновить базу",
                "3.Выход",
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


loop = asyncio.get_event_loop()
task = asyncio.ensure_future(main())
loop.run_until_complete(task)
