from fuzzywuzzy import process
from typing import Union


class KeywordMatcher:
    @staticmethod 
    #FIXME: replace staticmethod to func. We have type error if replace.
    async def find_keywords(message_text, keywords) -> Union[str, None]:
        try:
            if not message_text or not keywords:
                return None
                
            lst_msg = message_text.split()
            for keyword in keywords:
                ratio = process.extract(keyword, lst_msg, limit=1)
                if ratio and ratio[0][1] > 92:
                    print(f"Сообщение содержит ключевое слово: {keyword}")
                    return keyword
            return None
        except (AttributeError, TypeError):
            return None