import asyncio
from pyrogram import Client
from pyrogram.errors import FloodWait
import json
import os
from tqdm import tqdm
import pyfiglet
import platform

ascii_art = pyfiglet.figlet_format("GrekF3", font="slant")
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
    print(f"Чатов загружено: {len(chats)}")
    print('Начинаю спам')
    await asyncio.sleep(5)


async def main():
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
                    await pbar.close()
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                finally:
                    await clear_console()
                    await spamer_bot(chats=chat)
        else:
            await spamer_bot(chats=chats)


loop = asyncio.get_event_loop()
task = asyncio.ensure_future(main())
loop.run_until_complete(task)