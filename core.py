import os

class SpamerSettings:
    def __init__(self, file_path='settings.txt'):
        self.phone = ''
        self.api_id = ''
        self.api_hash = ''
        self.timeout = ''
        self.load_settings_from_file(file_path)

    def load_settings_from_file(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    key, value = map(str.strip, line.split('='))
                    if hasattr(self, key):
                        setattr(self, key, value)
        else:
            print(f"File not found: {file_path}")

    def check_all_fields_filled(self):
        all_fields_filled = all([getattr(self, field) for field in vars(self)])
        return all_fields_filled

if __name__ == '__main__':
    # Укажите путь к файлу с настройками, если он не в том же каталоге, где и скрипт
    script_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_directory, 'settings.txt')
    
    settings = SpamerSettings(file_path)

    if settings.check_all_fields_filled():
        print("All fields are filled.")
    else:
        print("Some fields are not filled. Please check your settings.")
