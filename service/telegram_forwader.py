import asyncio
from typing import List

from data.telegram_client import TelegramClientManager
from service.keyword_matcher import KeywordMatcher
from service.message_processor import MessageProcessor
from service.message_processor import MessageIdInvalidError


class TelegramForwarder:
    def __init__(self, api_id, api_hash, phone_number):
        self.client_manager = TelegramClientManager(api_id, api_hash, phone_number)
        #FIXME: Type error here. When replace staticmethod to func.
        self.keyword_matcher = KeywordMatcher()
        self.message_processor = MessageProcessor(self.client_manager.client)

    async def list_chats(self) -> None:
        await self.client_manager.connect_and_auth()
        dialogs = await self.client_manager.get_dialogs()
        
        with open(f"chats_of_{self.client_manager.phone_number}.txt", "w", 
                  encoding='utf-8') as chats_file:
            for dialog in dialogs:
                print(f"Chat ID: {dialog.id}, Title: {dialog.title}")
                chats_file.write(f"Chat ID: {dialog.id}, Title: {dialog.title}\n")
                
        print("Список групп распечатан!")

    async def forward_messages_to_channel(self, 
                        source_chat_ids: List[int], 
                        destination_channel_id: int, 
                        keywords: List[str]) -> None:
        await self.client_manager.connect_and_auth()
        
        last_message_ids = await self.message_processor.get_last_message_ids(source_chat_ids)
        
        while True:
            for source_chat_id in source_chat_ids:
                try:
                    messages = await self.client_manager.get_messages(
                        source_chat_id, 
                        min_id=last_message_ids[source_chat_id], 
                        limit=None
                    )
                except MessageIdInvalidError:
                    print('Сообщение с неправильным ID')
                    continue

                for message in reversed(messages): # type: ignore
                    forwarded = await self.message_processor.process_and_forward_message(
                        message, source_chat_id, destination_channel_id,
                        self.keyword_matcher, keywords
                    )
                    
                    if forwarded:
                        last_message_ids[source_chat_id] = max(
                            last_message_ids[source_chat_id], 
                            message.id
                        )

            await asyncio.sleep(3)