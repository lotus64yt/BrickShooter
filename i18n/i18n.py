import os
import json

class Translator:
    def __init__(self, locales_dir, lang):
        self.translations = {}
        lang_dir = locales_dir + "/" + lang
        if os.path.exists(lang_dir):
            files = os.listdir(lang_dir)
            for filename in files:
                file_path = lang_dir + "/" + filename
                if os.path.isfile(file_path):
                    f = open(file_path, 'r', encoding='utf-8')
                    data = json.load(f)
                    f.close()
                    for key in data:
                        self.translations[key] = data[key]

    def translate(self, key, arg1=None):
        keys = key.split('.')
        value = self.translations
        for k in keys:
            if k in value:
                value = value[k]
            else:
                return key
        
        if isinstance(value, str):
            if arg1 != None:
                return value.replace("{fps}", str(arg1))
            return value
        return str(value)

def create_translator(locales_dir, lang):
    t_obj = Translator(locales_dir, lang)
    return t_obj.translate
