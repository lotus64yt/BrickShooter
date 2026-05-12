import os
import json
def create_translator(locales_dir, lang):
    translations = {}
    lang_dir = os.path.join(locales_dir, lang)
    if os.path.exists(lang_dir):
        for filename in os.listdir(lang_dir):
            file_path = os.path.join(lang_dir, filename)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        translations.update(data)
                except Exception as e:
                    print(f"Error loading translation file {file_path}: {e}")

    def t(key, **kwargs):
        keys = key.split('.')
        value = translations
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return key
        if isinstance(value, str):
            try:
                return value.format(**kwargs)
            except KeyError:
                return value
        return str(value)
    return t
