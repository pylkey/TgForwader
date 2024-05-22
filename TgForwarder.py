import time
import asyncio
from telethon.sync import TelegramClient

class TelegramForwarder:
    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client = TelegramClient('session_' + phone_number, api_id, api_hash)

    async def list_chats(self):
        await self.client.connect()

        # Ensure you're authorized
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input('Введите код: '))

        # Get a list of all the dialogs (chats)
        dialogs = await self.client.get_dialogs()
        chats_file = open(f"chats_of_{self.phone_number}.txt", "w", encoding='utf-8')
        # Print information about each chat
        for dialog in dialogs:
            print(f"Chat ID: {dialog.id}, Title: {dialog.title}")
            chats_file.write(f"Chat ID: {dialog.id}, Title: {dialog.title} \n")
          

        print("List of groups printed successfully!")

    async def forward_messages_to_channel(self, source_chat_ids, destination_channel_id, keywords):
        await self.client.connect()

        # Ensure you're authorized
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input('Введите код: '))

        last_message_ids = {chat_id: (await self.client.get_messages(chat_id, limit=1))[0].id for chat_id in source_chat_ids}

        # last_message_id = (await self.client.get_messages(source_chat_id, limit=1))[0].id

        while True:
            print("Проверяем сообщения для пересылки...")
            # Get new messages since the last checked message
            # messages = await self.client.get_messages(source_chat_id, min_id=last_message_id, limit=None)
            for source_chat_id in source_chat_ids:
                messages = await self.client.get_messages(source_chat_id, min_id=last_message_ids[source_chat_id], limit=None)

                for message in reversed(messages):
                    # Check if the message text includes any of the keywords
                    if keywords:
                        if message.text and any(keyword in message.text.lower() for keyword in keywords):
                            print(f"Сообщение содержит следующие слова: {message.text}")

                            # Forward the message to the destination channel
                            await self.client.forward_messages(destination_channel_id, message.text)

                            print("Сообщение переслано")
                    else:
                            # Forward the message to the destination channel
                            await self.client.forward_messages(destination_channel_id, message.text)

                            print("Сообщение переслано")


                # Update the last message ID
                # last_message_id = max(last_message_id, message.id)
                    last_message_ids[source_chat_id] = max(last_message_ids[source_chat_id], message.id)

            # Add a delay before checking for new messages again
            await asyncio.sleep(5)  # Adjust the delay time as needed


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
        api_id = input("ВВедите ваш API ID: ")
        api_hash = input("Введите ваш API Hash: ")
        phone_number = input("Введите ваш номер телефона: ")
        # Write credentials to file for future use
        write_credentials(api_id, api_hash, phone_number)

    forwarder = TelegramForwarder(api_id, api_hash, phone_number)
    
    print("Выберете опции (ввести цифру):")
    print("1. Список чатов")
    print("2. Пересылать сообщения")
    
    choice = input("Введите свой выбор: ")
    
    if choice == "1":
        await forwarder.list_chats()
    elif choice == "2":
        source_chat_ids = list(map(int, input("Введите исходные (откуда будут пересылаться сообщения) chat ID через запятую: ").split(",")))
        destination_channel_id = int(input("Введите целевой (куда будут пересылаться сообщения) chat ID: "))
        print("Введите слова, если вы хотите пересылать сообщения содержащие эти слова или оставьте пустым, чтобы получать каждое сообщение")
        keywords = input("Печатайте слова разделяя их запятыми или оставьте пустым: ").split(",")
        
        await forwarder.forward_messages_to_channel(source_chat_ids, destination_channel_id, keywords)
    else:
        print("Неправильный выбор")

# Start the event loop and run the main function
if __name__ == "__main__":
    asyncio.run(main())