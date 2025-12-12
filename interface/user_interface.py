from data.credentials_manager import CredentialsManager
from service.telegram_forwader import TelegramForwarder


async def run_user_interface():
    """
    Взаимодействие с пользователем
    """
    api_id, api_hash, phone_number = CredentialsManager.read_credentials()

    if api_id is None or api_hash is None or phone_number is None:
        api_id = input("Введите ваш API ID: ")
        api_hash = input("Введите ваш API Hash: ")
        phone_number = input("Введите ваш номер телефона: ")
        CredentialsManager.write_credentials(api_id, api_hash, phone_number)

    forwarder = TelegramForwarder(api_id, api_hash, phone_number)
    
    print("Выберите опцию (ввести цифру):")
    print("1. Список чатов")
    print("2. Пересылать сообщения")
    
    choice = input("Введите ваш выбор: ")
    
    if choice == "1":
        await forwarder.list_chats()
    elif choice == "2":
        source_chat_ids = list(map(int, 
            input("Введите исходные chat ID через запятую: ").split(",")))
        destination_channel_id = int(input("Введите целевой chat ID: "))
        print("Введите слова, если вы хотите пересылать сообщения содержащие эти слова")
        print("или оставьте пустым, чтобы получать каждое сообщение")
        keywords_input = input("Печатайте слова разделяя их запятыми или оставьте пустым: ")
        keywords = keywords_input.split(",") if keywords_input.strip() else []
        
        await forwarder.forward_messages_to_channel(
            source_chat_ids, destination_channel_id, keywords
        )
    else:
        print("Неправильный выбор")