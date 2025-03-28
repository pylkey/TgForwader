import json
import asyncio
from telethon.sync import TelegramClient
# from fuzzywuzzy import process
from fuzzywuzzy import fuzz
from typing import Union
from telethon.tl.types import PeerChannel
from telethon.errors.rpcerrorlist import ChatForwardsRestrictedError, ChannelPrivateError, MessageIdInvalidError


MATCH_THRESHOLD = 80
DEST_GROUP_ID = -1002057223298
KEYWORDS = ['юрист','суд','аппеляция','процент','взыскать','получение','передача','дкп','дду','исполнительный лист',
            'собственник квартиры','собственности','осмотр','неустойка','стоимость','надзор','приемщик','квартира',
            'отзыв','новостройка','услуга','помощь','компании','черновая','предчистовая','профессиональная','заказать',
            'независимая','окна','застройщика','покупке','продаже','специалистами','специалист','нанять','профессиональные',
            'взыскание','компенсации','юридическое','ключи','мораторий','акт', 'приема-передачи','постамат','задержка',
            'приемка','обмер','замер','дизайн-проект','дизайн','проект','принять','недостатки','покраска','обоев','стен',
            'замена','ламинат','ремонт','отделочные','мастер','плитка','клининг','уборка','торт','тортик','кондиционер',
            'кондиционерщик','установка','мебель','кухня','потолок','натяжной','контакты','данные','оказывает',
            'порекомендуйте','посоветуйте','ванна','кварц','винил','кварцвинил','оценка']


class GetSettings:
    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client = TelegramClient('session_' + phone_number, api_id, api_hash)

        # Structure json 
        self.data = {
            'chanels':[],
            'dest_id':DEST_GROUP_ID,
            'keywords':KEYWORDS
        }

    async def get_list_chats(self, data) -> dict:
        # Get a list of all the dialogs (chats)
        dialogs = await self.client.get_dialogs()
        # Information about each chat
        for dialog in dialogs:
            data['chanels'].append({
                'id':dialog.id,
                'title':dialog.title
            })          
        print("Список групп распечатан!")
        return data
    
    async def write_setting(self, data) -> None:
        with open('settings.json', 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

        print("Данные успешно сохранены в settings.json")

    async def make_settings_file(self) -> None:
        await self.client.connect()

        # Ensure you're authorized
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input('Введите код: '))

        await self.get_list_chats(self.data)
        await self.write_setting(self.data)
        print('Проверить список групп в файле settings.json. Группы начинаются с "-100"')

        


class TelegramForwarder:
    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client = TelegramClient('session_' + phone_number, api_id, api_hash)

    
    async def find_keywords(self, message, keywords)->Union[str, None]:
        try:
            lst_msg = message.split()
            for keyword in keywords:
                ratio = fuzz.token_sort_ratio(keyword, lst_msg)
                if ratio > MATCH_THRESHOLD:
                    print(f"Сообщение содержит ключевое слово: {keyword}")
                    return keyword
            return None
        except AttributeError:
            return None

       
    async def last_message_ids(self, source_chat_ids:list) -> dict:
        """Get last message_ids"""
        last_message_ids = {}
        invalid_chats=[]
        for chat_id in source_chat_ids:
            try:
                messages = await self.client.get_messages(chat_id, limit=1)
                if messages:
                    last_message_ids[chat_id] = messages[0].id
            except ChannelPrivateError:
                print(f'У вас нет разрешения на доступ к каналу {chat_id}. Или вас забанили на нем. Чат убран из списка пересылаемых')
                invalid_chats.append(chat_id)
        # Delete invalid chats
        for invalid_chat in invalid_chats:
            source_chat_ids.remove(invalid_chat)

        return last_message_ids

    
    async def forward_messages_to_channel(self, 
                        source_chat_ids:list, 
                        destination_channel_id:list, 
                        keywords:list)->None:
        await self.client.connect()

        # Ensure you're authorized
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input('Введите код: '))

        last_message_ids = await self.last_message_ids(source_chat_ids)
        while True:
            # Get new messages since the last checked message
            for source_chat_id in source_chat_ids:
                try:
                    messages = await self.client.get_messages(source_chat_id, min_id=last_message_ids[source_chat_id], limit=None)
                except MessageIdInvalidError:
                    print('Сообщение с неправильным ID')

                for message in reversed(messages):    
                    # Check if the message text includes any of the keywords
                    try:
                        if keywords:
                            keyword = await self.find_keywords(message.text, keywords)
                            if isinstance(keyword, str):
                                # Forward the message to the destination channel with keywords and mark as read
                                await self.client.forward_messages(destination_channel_id, message.id, source_chat_id)
                                entity = await self.client.get_entity(PeerChannel(source_chat_id))
                                await self.client.send_message(
                                    destination_channel_id, 
                                    f'Переслано из {entity.title}, содержит слово {keyword}'
                                    )
                                await self.client.send_read_acknowledge(source_chat_id, message)

                                print(f"Сообщение {message.id} переслано из {entity.title} {source_chat_id}")
                        else:
                            # Forward the message to the destination channel without keywords
                            await self.client.forward_messages(destination_channel_id, message.id, source_chat_id)
                            entity = await self.client.get_entity(PeerChannel(source_chat_id))
                            await self.client.send_message(destination_channel_id, f'Переслано из {entity.title}')
                            await self.client.send_read_acknowledge(source_chat_id, message)

                            print(f"Сообщение {message.id} переслано из {source_chat_id}")

                    except ChatForwardsRestrictedError:
                        await self.client.send_message(destination_channel_id, f'Не могу переслать сообщение из закрытого канала {entity.title}')
                    except MessageIdInvalidError:
                        print('Неправильный ID сообщения')
        
                    # Update the last message ID
                    last_message_ids[source_chat_id] = max(last_message_ids[source_chat_id], message.id)

            # Add a delay before checking for new messages again
            await asyncio.sleep(3)  # Adjust the delay time as needed


# Function to read credentials from file
def read_credentials():
    try:
        with open("credentials.txt", "r") as file:
            lines = file.readlines()
            api_id = lines[0].strip()
            api_hash = lines[1].strip()
            phone_number = lines[2].strip()
            return api_id, api_hash, phone_number
    except FileNotFoundError:
        print("Credentials file not found.")
        return None, None, None

# Function to write credentials to file
def write_credentials(api_id, api_hash, phone_number):
    with open("credentials.txt", "w") as file:
        file.write(api_id + "\n")
        file.write(api_hash + "\n")
        file.write(phone_number + "\n")

async def main():
    # Attempt to read credentials from file
    api_id, api_hash, phone_number = read_credentials()

    # If credentials not found in file, prompt the user to input them
    if api_id is None or api_hash is None or phone_number is None:
        api_id = input("Введите ваш API ID: ")
        api_hash = input("Введите ваш API Hash: ")
        phone_number = input("Введите ваш номер телефона: ")
        # Write credentials to file for future use
        write_credentials(api_id, api_hash, phone_number)

    forwarder = TelegramForwarder(api_id, api_hash, phone_number)
    setup = GetSettings(api_id, api_hash, phone_number)
    
    print("Выберете опции (ввести цифру):")
    print("1. Заполнить список пересылаемых чатов")
    print("2. Пересылать сообщения")
    
    choice = input("Введите свой выбор: ")
    
    if choice == "1":
        await setup.make_settings_file()
    elif choice == "2":
        try:
            with open('settings.json', 'r', encoding='utf-8') as file:
                data = file.read()

                obj = json.loads(data)

                source_chat_ids = []
                for channel in obj['chanels']:
                    source_chat_ids.append(channel['id'])
                
                destination_channel_id = obj['dest_id']

                keywords = obj['keywords']
        except FileNotFoundError:
            exit('Проверте наличие файла "settings.json"')
        
        await forwarder.forward_messages_to_channel(source_chat_ids, destination_channel_id, keywords)
    else:
        print("Неправильный выбор")

# Start the event loop and run the main function
if __name__ == "__main__":
    asyncio.run(main())
