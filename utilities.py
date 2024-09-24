import os
import json
import sys
import re

class Markdowner:
    def __init__(self, output_path = "output.md"):
        self.output_path = output_path
        if not os.path.exists(self.output_path):
            with open(self.output_path, 'w') as f:
                f.write("")

    def write(self, text):
        with open(self.output_path, 'a') as f:
            f.write(f"{text}\n")
    
    def write_heading(self, text, level=1):
        self.write(f"\n{'#' * level} {text}\n")

    def write_code_block(self, code, language="smali"):
        self.write(f"\n```{language}\n{code}```\n")
    
    def write_bullet(self, text):
        self.write(f"- {text}")
    
    def clear(self):
        with open(self.output_path, 'w') as f:
            f.write("")


class OSUtils:
    @staticmethod
    def run_unix_command(command: str):
        try: 
            os.system(command)
        except Exception as e:
            print(f"Are you running in the correct environment? Error: {e}")
    
    @staticmethod
    def rename_files_in_folder(folder_path: str):
        illegal_filepath_symbols = [" ", "(", ")", "[", "]", "{", "}", "!", "@", "#", "$", "%", "^", "&", "*", "+", "=", "?", "<", ">", ",", ";", ":", "'", "`", "~", "|"]
        for filename in os.listdir(folder_path):
            old_path = os.path.join(folder_path, filename)
            new_path = ''.join(e for e in old_path if e not in illegal_filepath_symbols)
            os.rename(old_path, new_path)
                
            # re.sub(r'[^\w\s]', '', filename)
            # os.rename(folder_path + "/" + filename, folder_path + "/" + filename.replace(" ", "-"))
            

    
    @staticmethod
    def find_how_many_files_are_in_a_folder(folder_path: str):
        return len(os.listdir(folder_path))
    
    @staticmethod
    def read_file(file_path: str):
        with open(file_path, 'r') as file:
            return file.read()
    
    @staticmethod
    def isWindows():
        return sys.platform.startswith('win')
    
    @staticmethod
    def isLinux():
        return sys.platform.startswith('linux')

class JSONCreator:
    def __init__(self, output_path):
        self.output_path = output_path
    
    def write(self, data):
        with open(self.output_path, 'w') as f:
            json.dump(data, f)
    
    def read(self):
        with open(self.output_path, 'r') as f:
            return json.load(f)

class JSONPermissions:
    def __init__(self, output_path = "results/permissions-count.json"):
        self.output_path = output_path
        self.sensitive_permissions =  [
            'android.permission.CAMERA',
            'android.permission.RECORD_AUDIO',
            'android.permission.READ_SMS',
            'android.permission.READ_CONTACTS',
            'android.permission.READ_PHONE_STATE',
            'android.permission.READ_CALL_LOG',
            'android.permission.READ_EXTERNAL_STORAGE',
            'android.permission.WRITE_EXTERNAL_STORAGE',
            'android.permission.ACCESS_FINE_LOCATION',
            'android.permission.ACCESS_COARSE_LOCATION',
            'android.permission.CALL_PHONE',
            'android.permission.SEND_SMS',
            'android.permission.INTERNET'
        ]
        permissions_dict = {permission: 0 for permission in self.sensitive_permissions}
        with open(self.output_path, 'w') as f:
            json_string = json.dumps(permissions_dict, indent=4)
            f.write(json_string)
    
    def read(self):
        with open(self.output_path, 'r') as f:
            return json.load(f)
    
    def reset(self):
        permissions_dict = {permission: 0 for permission in self.sensitive_permissions}
        with open(self.output_path, 'w') as f:
            json_string = json.dumps(permissions_dict, indent=4)
            f.write(json_string)

    def write(self, permissions_dict):
        previous_permissions_dict = self.read()
        with open(self.output_path, 'w') as f:
            for permission in permissions_dict:
                previous_permissions_dict[permission] += permissions_dict[permission]
            json.dump(previous_permissions_dict, f)
    
    def addInternet(self):
        self.write({"android.permission.INTERNET": 1})



if __name__ == "__main__":
    OSUtils.rename_files_in_folder("apps")