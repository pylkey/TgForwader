class CredentialsManager:
    @staticmethod
    def read_credentials(filename="credentials.txt"):
        try:
            with open(filename, "r", encoding='utf-8') as file:
                lines = file.readlines()
                api_id = lines[0].strip()
                api_hash = lines[1].strip()
                phone_number = lines[2].strip()
                return api_id, api_hash, phone_number
        except FileNotFoundError:
            print("Файл с учетными данными не найден.")
            return None, None, None

    @staticmethod
    def write_credentials(api_id, api_hash, phone_number, filename="credentials.txt"):
        with open(filename, "w", encoding='utf-8') as file:
            file.write(f"{api_id}\n{api_hash}\n{phone_number}\n")