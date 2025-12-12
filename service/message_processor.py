from typing import List, Dict
from telethon.errors.rpcerrorlist import ChatForwardsRestrictedError, MessageIdInvalidError, ChannelPrivateError
from telethon.tl.types import PeerChannel


class MessageProcessor:
    def __init__(self, telegram_client):
        self.client = telegram_client

    async def get_last_message_ids(self, source_chat_ids: List[int]) -> Dict[int, int]:
        last_message_ids = {}
        invalid_chats = []
        
        for chat_id in source_chat_ids:
            try:
                messages = await self.client.get_messages(chat_id, limit=1)
                if messages:
                    last_message_ids[chat_id] = messages[0].id
            except ChannelPrivateError:
                print(f'Нет доступа к каналу {chat_id}. Чат удален из списка.')
                invalid_chats.append(chat_id)
                
        for invalid_chat in invalid_chats:
            source_chat_ids.remove(invalid_chat)
            
        return last_message_ids

    async def process_and_forward_message(self, message, source_chat_id, 
                                          destination_channel_id, 
                                          keyword_matcher, keywords):
        try:
            if keywords:
                keyword = await keyword_matcher.find_keywords(message.text, keywords)
                if keyword:
                    await self._forward_with_keyword(message, source_chat_id, 
                                                    destination_channel_id, keyword)
                    return True
                return False
            else:
                await self._forward_without_keyword(message, source_chat_id, 
                                                   destination_channel_id)
                return True
                
        except ChatForwardsRestrictedError:
            entity = await self.client.get_entity(PeerChannel(source_chat_id))
            await self.client.send_message(
                destination_channel_id, 
                f'Не могу переслать сообщение из закрытого канала {entity.title}'
            )
        except MessageIdInvalidError:
            print('Неправильный ID сообщения')
            
        return False

    async def _forward_with_keyword(self, message, source_chat_id, 
                                   destination_channel_id, keyword):
        await self.client.forward_messages(destination_channel_id, 
                                          message.id, source_chat_id)
        entity = await self.client.get_entity(PeerChannel(source_chat_id))
        await self.client.send_message(
            destination_channel_id,
            f'Переслано из {entity.title}, содержит слово {keyword}'
        )
        await self.client.send_read_acknowledge(source_chat_id, message)
        print(f"Сообщение {message.id} переслано из {source_chat_id}")

    async def _forward_without_keyword(self, message, source_chat_id, 
                                      destination_channel_id):
        await self.client.forward_messages(destination_channel_id, 
                                          message.id, source_chat_id)
        entity = await self.client.get_entity(PeerChannel(source_chat_id))
        await self.client.send_message(destination_channel_id, 
                                      f'Переслано из {entity.title}')
        await self.client.send_read_acknowledge(source_chat_id, message)
        print(f"Сообщение {message.id} переслано из {source_chat_id}")