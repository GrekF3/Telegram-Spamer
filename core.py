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
            with open(file_path, "w", encoding="utf-8") as file:
                file.write("phone=\napi_id=\napi_hash=\ntimeout=\n")

    def check_all_fields_filled(self):
        all_fields_filled = all([getattr(self, field) for field in vars(self)])
        return all_fields_filled

