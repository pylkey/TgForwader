from telethon.sync import TelegramClient


class TelegramClientManager:
    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client = TelegramClient(f'session_{phone_number}', api_id, api_hash)

    async def connect_and_auth(self):
        await self.client.connect()
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            code = input('Введите код: ')
            await self.client.sign_in(self.phone_number, code)

    async def get_dialogs(self):
        return await self.client.get_dialogs()

    async def get_messages(self, chat_id, **kwargs):
        return await self.client.get_messages(chat_id, **kwargs)

    async def forward_messages(self, destination_id, message_id, source_id):
        return await self.client.forward_messages(destination_id, message_id, source_id)

    async def get_entity(self, peer):
        return await self.client.get_entity(peer)

    async def send_message(self, destination_id, text):
        return await self.client.send_message(destination_id, text)

    async def send_read_acknowledge(self, chat_id, message):
        return await self.client.send_read_acknowledge(chat_id, message)